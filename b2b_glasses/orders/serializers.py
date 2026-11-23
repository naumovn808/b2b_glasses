# from rest_framework import serializers
# from .models import Order, OrderItem, CustomOrder
# from catalog.models import Frame, Lens
# from django.contrib.contenttypes.models import ContentType
# import logging

# logger = logging.getLogger(__name__)


# class AddCartItemSerializer(serializers.Serializer):
#     """
#     Сериализатор для POST /api/v1/orders/cart/add/
#     Принимает "frame" или "lens" и ID.
#     """

#     product_type = serializers.ChoiceField(choices=["frame", "lens"])
#     product_id = serializers.IntegerField()
#     quantity = serializers.IntegerField(min_value=1, default=1)

#     def validate(self, data):
#         """Проверяем, что товар существует в БД."""
#         product_type = data.get("product_type")
#         product_id = data.get("product_id")

#         try:
#             if product_type == "frame":
#                 model = Frame
#             elif product_type == "lens":
#                 model = Lens
#             else:
#                 raise serializers.ValidationError("Неверный product_type.")

#             # Ищем товар
#             product = model.objects.get(pk=product_id)
#             # Сохраняем "найденный" объект, чтобы передать его в View
#             data["product_instance"] = product

#         except model.DoesNotExist:
#             raise serializers.ValidationError(
#                 f"{product_type} с ID {product_id} не найден."
#             )
#         except Exception as e:
#             raise serializers.ValidationError(f"Ошибка валидации: {e}")

#         return data


# class ProductRelatedField(serializers.RelatedField):
#     """
#     Кастомное поле для GFK (GenericForeignKey),
#     чтобы в API красиво отображались Frame/Lens.
#     """

#     def to_representation(self, value):
#         if isinstance(value, Frame):
#             return f"Оправа: {value.name} (ID: {value.pk})"
#         elif isinstance(value, Lens):
#             return f"Линза: {value.series.name} (SPH: {value.sph}, CYL: {value.cyl})"
#         return f"Неизвестный товар: {value.pk}"


# class OrderItemSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для ОДНОЙ Позиции Заказа (в Корзине)
#     """

#     product = ProductRelatedField(read_only=True)
#     image = serializers.SerializerMethodField()
#     stock = serializers.SerializerMethodField()
#     total_price = serializers.DecimalField(
#         max_digits=12, decimal_places=2, read_only=True
#     )

#     class Meta:
#         model = OrderItem
#         fields = (
#             "id",
#             "product",
#             "quantity",
#             "price_at_order",
#             "total_price",
#             "stock",
#             "image",
#         )

#     def get_image(self, obj):
#         product = obj.product
#         if not product:
#             return None

#         images = getattr(product, "images", None)
#         if images is None:
#             return None

#         first_image = images.order_by("order", "id").first()
#         if not first_image or not first_image.image:
#             return None

#         request = self.context.get("request")
#         url = first_image.image.url
#         if request:
#             return request.build_absolute_uri(url)
#         return url

#     def get_stock(self, obj):
#         product = obj.product
#         if not product:
#             return None

#         return getattr(product, "stock", None)


# class OrderSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для Заказа/Корзины
#     """

#     items = OrderItemSerializer(many=True, read_only=True)

#     class Meta:
#         model = Order
#         fields = ("id", "user", "status", "total_price", "created_at", "items")


# # --- НОВЫЙ СЕРИАЛИЗАТОР ---
# class CustomOrderSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для создания индивидуального заказа (через бота)
#     """

#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())

#     class Meta:
#         model = CustomOrder
#         fields = (
#             "id",
#             "user",
#             "series",
#             "sph",
#             "cyl",
#             "dia",
#             "design",
#             "photochrom",
#             "status",
#             "created_at",
#         )
#         read_only_fields = ("id", "status", "created_at")
# from rest_framework import serializers
# from .models import Order, OrderItem, CustomOrder
# from catalog.models import Frame, Lens
# from django.contrib.contenttypes.models import ContentType
# import logging

# logger = logging.getLogger(__name__)


# class AddCartItemSerializer(serializers.Serializer):
#     """
#     Сериализатор для POST /api/v1/orders/cart/add/
#     Принимает "frame" или "lens" и ID.
#     """
#     product_type = serializers.ChoiceField(choices=['frame', 'lens'])
#     product_id = serializers.IntegerField()
#     quantity = serializers.IntegerField(min_value=1, default=1)

#     def validate(self, data):
#         """Проверяем, что товар существует в БД."""
#         product_type = data.get('product_type')
#         product_id = data.get('product_id')

#         try:
#             if product_type == 'frame':
#                 model = Frame
#             elif product_type == 'lens':
#                 model = Lens
#             else:
#                 raise serializers.ValidationError("Неверный product_type.")

#             # Ищем товар
#             product = model.objects.get(pk=product_id)
#             # Сохраняем "найденный" объект, чтобы передать его в View
#             data['product_instance'] = product

#         except model.DoesNotExist:
#             raise serializers.ValidationError(
#                 f"{product_type} с ID {product_id} не найден.")
#         except Exception as e:
#             raise serializers.ValidationError(f"Ошибка валидации: {e}")

#         return data


# class ProductRelatedField(serializers.RelatedField):
#     """
#     Кастомное поле для GFK (GenericForeignKey),
#     чтобы в API красиво отображались Frame/Lens.
#     """

#     def to_representation(self, value):
#         if isinstance(value, Frame):
#             return f"Оправа: {value.name} (ID: {value.pk})"
#         elif isinstance(value, Lens):
#             return f"Линза: {value.series.name} (SPH: {value.sph}, CYL: {value.cyl})"
#         return f"Неизвестный товар: {value.pk}"


# class OrderItemSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для ОДНОЙ Позиции Заказа (в Корзине)
#     """
#     product = ProductRelatedField(read_only=True)
#     total_price = serializers.DecimalField(
#         max_digits=12, decimal_places=2, read_only=True)

#     class Meta:
#         model = OrderItem
#         fields = ('id', 'product', 'quantity', 'price_at_order', 'total_price')


# class OrderSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для Заказа/Корзины
#     """
#     items = OrderItemSerializer(many=True, read_only=True)

#     class Meta:
#         model = Order
#         fields = ('id', 'user', 'status', 'total_price', 'created_at', 'items')


# # --- НОВЫЙ СЕРИАЛИЗАТОР ---
# class CustomOrderSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для создания индивидуального заказа (через бота)
#     """
#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())

#     class Meta:
#         model = CustomOrder
#         fields = (
#             'id', 'user',
#             'series', 'sph', 'cyl', 'dia',
#             'design', 'photochrom',
#             'status', 'created_at'
#         )
#         read_only_fields = ('id', 'status', 'created_at')
from rest_framework import serializers
from .models import Order, OrderItem, CustomOrder
from catalog.models import Frame, Lens
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger(__name__)


class AddCartItemSerializer(serializers.Serializer):
    """
    Сериализатор для POST /api/v1/orders/cart/add/
    Принимает "frame" или "lens" и ID.
    """

    product_type = serializers.ChoiceField(choices=["frame", "lens"])
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        """Проверяем, что товар существует в БД и доступен в нужном количестве."""
        product_type = data.get("product_type")
        product_id = data.get("product_id")
        quantity = data.get("quantity", 1)

        try:
            if product_type == "frame":
                model = Frame
            elif product_type == "lens":
                model = Lens
            else:
                raise serializers.ValidationError("Неверный product_type.")

            # Ищем товар
            product = model.objects.get(pk=product_id)

            if product.stock <= 0:
                raise serializers.ValidationError(
                    {"quantity": "Товар отсутствует на складе."}
                )
            if quantity > product.stock:
                raise serializers.ValidationError(
                    {
                        "quantity": f"Недостаточно остатка на складе. Доступно: {product.stock} шт."
                    }
                )

            # Сохраняем "найденный" объект, чтобы передать его в View
            data["product_instance"] = product

        except model.DoesNotExist:
            raise serializers.ValidationError(
                f"{product_type} с ID {product_id} не найден."
            )
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(f"Ошибка валидации: {e}")

        return data


class ProductRelatedField(serializers.RelatedField):
    """
    Кастомное поле для GFK (GenericForeignKey),
    чтобы в API красиво отображались Frame/Lens.
    """

    def to_representation(self, value):
        if isinstance(value, Frame):
            return f"Оправа: {value.name} (ID: {value.pk})"
        elif isinstance(value, Lens):
            return f"Линза: {value.series.name} (SPH: {value.sph}, CYL: {value.cyl})"
        return f"Неизвестный товар: {value.pk}"


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ОДНОЙ Позиции Заказа (в Корзине)
    """

    product = ProductRelatedField(read_only=True)
    stock = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    total_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "stock",
            "image",
            "quantity",
            "price_at_order",
            "total_price",
        )

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Количество должно быть не меньше 1.")
        if self.instance is not None and self.instance.product is not None:
            available = getattr(self.instance.product, "stock", 0)
            if available <= 0:
                raise serializers.ValidationError("Товар отсутствует на складе.")
            if value > available:
                raise serializers.ValidationError(
                    f"Недостаточно остатка на складе. Доступно: {available} шт."
                )
        return value

    def get_stock(self, obj):
        product = obj.product
        if not product:
            return None
        return getattr(product, "stock", None)

    def get_image(self, obj):
        product = obj.product
        if not product:
            return None

        images = getattr(product, "images", None)
        if images is None:
            return None

        first_image = images.order_by("order", "id").first()
        if not first_image or not first_image.image:
            return None

        request = self.context.get("request")
        url = first_image.image.url
        if request:
            return request.build_absolute_uri(url)
        return url


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Заказа/Корзины
    """

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "id_1c",
            "doc_number_1c",
            "user",
            "status",
            "total_price",
            "created_at",
            "items",
        )


# --- НОВЫЙ СЕРИАЛИЗАТОР ---
class CustomOrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания индивидуального заказа (через бота)
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CustomOrder
        fields = (
            "id",
            "user",
            "series",
            "sph",
            "cyl",
            "dia",
            "design",
            "photochrom",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "status", "created_at")
