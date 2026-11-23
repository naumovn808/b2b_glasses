import logging
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone
from django.db.models import Q

from .models import Order, OrderItem, CustomOrder
from .serializers import (
    OrderSerializer,
    AddCartItemSerializer,
    OrderItemSerializer,
    CustomOrderSerializer,
)
from catalog.models import Frame, Lens
from catalog.one_c_sync import apply_stock_updates
from api.one_c_client import OneCAPIError, OneCConnectionError
from .one_c_orders import OrderCustomerConfigError, submit_order_to_1c

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)


class CartView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    @swagger_auto_schema(
        tags=["Orders (Корзина)"],
        operation_summary="1. Получить текущую корзину",
        operation_description="Получает 'активную' корзину (status='cart') пользователя. Если корзины нет, создает новую пустую.",
        responses={200: OrderSerializer, 401: "Не аутентифицирован"},
    )
    def get_object(self):
        user = self.request.user
        obj, created = Order.objects.get_or_create(
            user=user, status=Order.OrderStatus.CART
        )
        if created:
            logger.info(
                f"Создана новая пустая корзина для {user.username} (order_id={obj.pk})"
            )
        return obj


class AddCartItemView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Orders (Корзина)"],
        operation_summary="2. Добавить/Обновить товар в корзине",
        operation_description="Добавляет товар в корзину. Если товар уже есть, обновляет его количество.",
        request_body=AddCartItemSerializer,
        responses={
            201: OrderSerializer,
            400: "Ошибка валидации (напр. 'product_id не найден')",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = AddCartItemSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Ошибка добавления в корзину (400): {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product = serializer.validated_data["product_instance"]
        quantity = serializer.validated_data["quantity"]
        user = request.user

        cart, _ = Order.objects.get_or_create(user=user, status=Order.OrderStatus.CART)

        content_type = ContentType.objects.get_for_model(product)

        try:
            order_item = OrderItem.objects.get(
                order=cart, content_type=content_type, object_id=product.pk
            )
            order_item.quantity = quantity
            order_item.price_at_order = product.price
            order_item.save()
            logger.info(f"Обновлено кол-во товара {str(product)} в корзине {cart.pk}")

        except OrderItem.DoesNotExist:
            order_item = OrderItem.objects.create(
                order=cart,
                product=product,
                quantity=quantity,
                price_at_order=product.price,
            )
            logger.info(f"Добавлен новый товар {str(product)} в корзину {cart.pk}")

        cart.update_total_price()

        return Response(
            OrderSerializer(cart, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class ClearCartView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Orders (Корзина)"],
        operation_summary="3. Очистить корзину (полностью)",
        responses={204: "No Content", 404: "Корзина не найдена"},
    )
    def delete(self, request, *args, **kwargs):
        user = request.user
        try:
            cart = Order.objects.get(user=user, status=Order.OrderStatus.CART)
        except Order.DoesNotExist:
            return Response(
                {"error": "Корзина не найдена."}, status=status.HTTP_404_NOT_FOUND
            )

        cart.items.all().delete()
        cart.update_total_price()
        logger.info(f"Корзина #{cart.pk} для {user.username} была очищена.")

        return Response(status=status.HTTP_204_NO_CONTENT)


class RemoveCartItemView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = OrderItem.objects.all()

    @swagger_auto_schema(
        tags=["Orders (Корзина)"],
        operation_summary="4. Удалить 1 позицию из корзины (по OrderItem ID)",
        operation_description="Принимает ID *позиции заказа* (OrderItem.id).",
        responses={204: "No Content", 404: "Позиция заказа не найдена"},
    )
    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(
            order__user=user, order__status=Order.OrderStatus.CART
        )

    def perform_destroy(self, instance):
        cart = instance.order
        super().perform_destroy(instance)
        # Важно: пересчитываем сумму после удаления
        cart.update_total_price()
        logger.info(f"Удален товар {instance.pk} из корзины {cart.pk}")


class UpdateCartItemView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    @swagger_auto_schema(
        tags=["Orders (Корзина)"],
        operation_summary="5. Изменить кол-во товара (по OrderItem ID)",
        operation_description="Позволяет изменить 'quantity' у конкретной записи в корзине. Используйте PATCH.",
        responses={200: OrderSerializer, 404: "Позиция не найдена"},
    )
    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(
            order__user=user, order__status=Order.OrderStatus.CART
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.product is not None:
            instance.price_at_order = instance.product.price
            instance.save(update_fields=["price_at_order"])
        instance.order.update_total_price()
        logger.info(
            f"В корзине {instance.order.pk} обновлено кол-во товара {instance.pk} -> {instance.quantity}"
        )


class CheckoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Orders (Корзина)"],
        operation_summary="6. Оформить заказ (Checkout)",
        operation_description=(
            "Проверяет остатки, синхронно отправляет заказ в 1С (POST /v1/orders), "
            "обновляет остатки и переводит корзину в статус 'pending'."
        ),
        request_body=None,
        responses={
            200: "Заказ оформлен",
            400: "Ошибка валидации",
            422: "Недостаточно остатков или ошибка данных в 1С",
            502: "Ошибка на стороне 1С",
            503: "Сервис 1С временно недоступен",
        },
    )
    def post(self, request, *args, **kwargs):
        user = request.user

        # Шаг 1. Атомарно проверяем корзину и локальные остатки до отправки в 1С
        with transaction.atomic():
            try:
                cart = (
                    Order.objects.select_for_update(of=("self",))
                    .select_related("user__company")
                    .get(user=user, status=Order.OrderStatus.CART)
                )
            except Order.DoesNotExist:
                return Response(
                    {"error": "Корзина не найдена или пуста."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            items = list(cart.items.all())
            if not items:
                return Response(
                    {"error": "Нельзя оформить пустую корзину."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            company = getattr(user, "company", None)
            if not company or not company.external_id:
                return Response(
                    {
                        "status": "error",
                        "error_code": "CUSTOMER_NOT_CONFIGURED",
                        "error": "У вашей компании не указан идентификатор 1С. Обратитесь к менеджеру.",
                        "message": "У вашей компании не указан идентификатор 1С. Обратитесь к менеджеру.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            out_of_stock = []
            for item in items:
                product = item.product
                if product is None:
                    out_of_stock.append(
                        {
                            "id_1c": None,
                            "requested": item.quantity,
                            "stock": 0,
                        }
                    )
                    continue

                if product.stock <= 0 or item.quantity > product.stock:
                    out_of_stock.append(
                        {
                            "id_1c": product.id_1c,
                            "requested": item.quantity,
                            "stock": product.stock,
                        }
                    )
                    continue

                if item.price_at_order != product.price:
                    item.price_at_order = product.price
                    item.save(update_fields=["price_at_order"])

            if out_of_stock:
                return Response(
                    {
                        "status": "error",
                        "error_code": "PRODUCT_OUT_OF_STOCK",
                        "error": "Недостаточно остатка по ряду позиций",
                        "message": "Недостаточно остатка по ряду позиций",
                        "updated_stocks": out_of_stock,
                    },
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            cart.update_total_price()

        # Шаг 2. Синхронно отправляем заказ в 1С (вне блокировки транзакции БД)
        try:
            one_c_response = submit_order_to_1c(cart)
        except OrderCustomerConfigError as exc:
            return Response(
                {
                    "status": "error",
                    "error_code": "CUSTOMER_NOT_CONFIGURED",
                    "error": str(exc),
                    "message": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except OneCConnectionError as exc:
            logger.error("Checkout #%s: 1С недоступна: %s", cart.pk, exc)
            return Response(
                {
                    "status": "error",
                    "error_code": exc.error_code or "ONE_C_UNAVAILABLE",
                    "error": "Сервис 1С временно недоступен. Попробуйте оформить заказ позже.",
                    "message": "Сервис 1С временно недоступен. Попробуйте оформить заказ позже.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except OneCAPIError as exc:
            updated_stocks = exc.payload.get("updated_stocks") or []
            if exc.error_code == "PRODUCT_OUT_OF_STOCK":
                if updated_stocks:
                    apply_stock_updates(updated_stocks)
                return Response(
                    {
                        "status": "error",
                        "order_id_site": cart.pk,
                        "error_code": "PRODUCT_OUT_OF_STOCK",
                        "error": exc.message,
                        "message": exc.message,
                        "updated_stocks": updated_stocks,
                    },
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            http_status = (
                status.HTTP_422_UNPROCESSABLE_ENTITY
                if exc.status_code and 400 <= exc.status_code < 500
                else status.HTTP_502_BAD_GATEWAY
            )
            return Response(
                {
                    "status": "error",
                    "order_id_site": cart.pk,
                    "error_code": exc.error_code or "ONE_C_ERROR",
                    "error": exc.message,
                    "message": exc.message,
                    "updated_stocks": updated_stocks,
                },
                status=http_status,
            )

        # Шаг 3. Фиксируем заказ и точечно обновляем остатки из ответа 1С
        updated_stocks = one_c_response.get("updated_stocks") or []
        if updated_stocks:
            apply_stock_updates(updated_stocks)

        with transaction.atomic():
            cart.status = Order.OrderStatus.PENDING
            cart.id_1c = one_c_response.get("order_id_1c") or cart.id_1c
            cart.doc_number_1c = (
                one_c_response.get("doc_number_1c") or cart.doc_number_1c
            )
            cart.updated_at = timezone.now()
            cart.save(update_fields=["status", "id_1c", "doc_number_1c", "updated_at"])

        logger.info(
            "Заказ #%s оформлен пользователем %s (1C doc=%s, total=%s).",
            cart.pk,
            user.username,
            cart.doc_number_1c,
            cart.total_price,
        )
        serializer = OrderSerializer(cart, context={"request": request})

        return Response(
            {
                "message": one_c_response.get("message") or "Заказ успешно оформлен",
                "order_id": cart.pk,
                "order_id_1c": cart.id_1c,
                "doc_number_1c": cart.doc_number_1c,
                "cart": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class OrderHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    @swagger_auto_schema(
        tags=["Orders (История)"],
        operation_summary="7. Получить историю заказов",
        responses={200: OrderSerializer(many=True)},
    )
    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .exclude(status=Order.OrderStatus.CART)
            .order_by("-created_at")
        )


# --- НОВЫЙ VIEW: СОЗДАНИЕ ИНДИВИДУАЛЬНОГО ЗАКАЗА ---
class CreateCustomOrderView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomOrderSerializer

    @swagger_auto_schema(
        tags=["Orders (Индивидуальные)"],
        operation_summary="Создать индивидуальный заказ (Custom)",
        operation_description="Создает заявку на линзы с произвольными параметрами.",
        responses={201: CustomOrderSerializer},
    )
    def perform_create(self, serializer):
        # Пользователь подставляется автоматически через HiddenField
        serializer.save()
