from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# --- 1. Импортируем модели, на которые ссылаемся ---
from catalog.models import Frame, Lens


class Order(models.Model):
    """
    Модель Заказа (Обычная корзина).
    """
    class OrderStatus(models.TextChoices):
        CART = 'cart', 'В корзине'
        PENDING = 'pending', 'В ожидании (Оформлен)'
        COMPLETED = 'completed', 'Выполнен'
        CANCELLED = 'cancelled', 'Отменен'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="orders"
    )
    status = models.CharField(
        max_length=10,
        choices=OrderStatus.choices,
        default=OrderStatus.CART,
        verbose_name="Статус"
    )

    total_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Итоговая цена"
    )
    id_1c = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="ID заказа в 1С",
    )
    doc_number_1c = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Номер документа в 1С",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Заказ (Каталог)"
        verbose_name_plural = "Заказы (Каталог)"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.pk} ({self.user.username}) - {self.get_status_display()}"

    def update_total_price(self):
        """Пересчитывает итоговую цену заказа."""
        total = sum(item.total_price for item in self.items.all())
        self.total_price = total
        self.save()


class OrderItem(models.Model):
    """
    Один товар (Линза ИЛИ Оправа) в Заказе.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name="Заказ",
        related_name="items"
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField(
        default=1, verbose_name="Количество")
    price_at_order = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Цена (на момент заказа)"
    )

    @property
    def total_price(self):
        return self.quantity * self.price_at_order

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
        unique_together = ('order', 'content_type', 'object_id')

    def __str__(self):
        if isinstance(self.product, Frame):
            product_name = self.product.name
        elif isinstance(self.product, Lens):
            product_name = str(self.product)
        else:
            product_name = "Неизвестный товар"

        return f"{product_name} (x{self.quantity})"


# --- НОВАЯ МОДЕЛЬ: ИНДИВИДУАЛЬНЫЙ ЗАКАЗ ---
class CustomOrder(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новая заявка'
        PROCESSING = 'processing', 'В обработке'
        COMPLETED = 'completed', 'Выполнен'
        CANCELLED = 'cancelled', 'Отменен'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="custom_orders"
    )

    # Параметры из фильтра (то, что искали)
    series = models.CharField(max_length=100, verbose_name="Серия (желаемая)")
    sph = models.CharField(max_length=50, verbose_name="SPH")
    cyl = models.CharField(max_length=50, verbose_name="CYL")
    dia = models.CharField(
        max_length=50, verbose_name="DIA", blank=True, null=True)

    # Доп. параметры (ручной ввод)
    design = models.CharField(max_length=255, verbose_name="Дизайн")
    photochrom = models.CharField(max_length=255, verbose_name="Фотохром")

    comment = models.TextField(
        verbose_name="Комментарий менеджера", blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Статус"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Заказ (Индивидуальный)"
        verbose_name_plural = "Заказы (Индивидуальные)"
        ordering = ['-created_at']

    def __str__(self):
        return f"Custom #{self.pk} - {self.user.username}"
