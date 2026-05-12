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
from .ftp_uploader import schedule_ftp_upload

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
        instance.order.update_total_price()
        logger.info(
            f"В корзине {instance.order.pk} обновлено кол-во товара {instance.pk} -> {instance.quantity}"
        )


class CheckoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Orders (Корзина)"],
        operation_summary="6. Оформить заказ (Checkout)",
        operation_description="Превращает 'Корзину' (status='cart') в 'Заказ' (status='pending').",
        request_body=None,
        responses={200: "Заказ оформлен", 400: "Ошибка"},
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            cart = Order.objects.get(user=user, status=Order.OrderStatus.CART)
        except Order.DoesNotExist:
            return Response(
                {"error": "Корзина не найдена или пуста."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not cart.items.exists():
            return Response(
                {"error": "Нельзя оформить пустую корзину."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            cart.status = Order.OrderStatus.PENDING
            cart.updated_at = timezone.now()
            cart.save()

        order_items = []
        for item in cart.items.all():
            try:
                product_str = str(item.product)
            except Exception:
                product_str = (
                    f"content_type={item.content_type_id}, object_id={item.object_id}"
                )
            order_items.append(
                f"{product_str} x{item.quantity} @ {item.price_at_order}"
            )

        print(
            f"Заказ #{cart.pk} оформлен пользователем {user.username}. "
            f"total_price={cart.total_price}, items_count={cart.items.count()}, "
            f"items=[{'; '.join(order_items)}]"
        )
        serializer = OrderSerializer(cart, context={"request": request})
        schedule_ftp_upload(cart)

        return Response(
            {
                "message": "Заказ успешно оформлен",
                "order_id": cart.pk,
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
