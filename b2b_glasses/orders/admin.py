from django.contrib import admin
from .models import Order, OrderItem
from users.models import Company  # <--- 1. Импортируем Компании


class OrderItemInline(admin.TabularInline):
    """
    Показывает Позиции Заказа (Товары) 
    ВНУТРИ страницы Заказа. (Без изменений)
    """
    model = OrderItem
    fields = ('product', 'quantity', 'price_at_order', 'total_price')
    readonly_fields = ('product', 'quantity', 'price_at_order', 'total_price')
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    # --- (list_display, list_filter, search_fields, inlines... без изменений) ---
    list_display = (
        'id',
        'user',
        'get_company',  # <-- ДОБАВЛЕНО
        'status',
        'total_price',
        'created_at'
    )
    # ---

    list_filter = (
        'status',
        'user__company',  # <-- (Goal 5) Фильтр по Компании
        'created_at'
    )
    search_fields = (
        'id',
        'user__username',
        'user__phone_number',
        'user__company__name'  # <-- (Goal 5) Поиск по Компании
    )

    inlines = [OrderItemInline]

    fieldsets = (
        ('Детали Заказа', {
            'fields': ('status', 'total_price', 'created_at', 'updated_at')
        }),
        ('Контрагент (Пользователь)', {
            'fields': ('user', 'get_company')  # <-- ДОБАВЛЕНО
        }),
    )
    # ---

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == 'cart':
            return True  # Разрешаем удалять "Корзины"
        return False  # Запрещаем удалять "Оформленные"

    # --- ИЗМЕНЕНИЕ (Goal 4): Делаем Статус редактируемым ---
    def get_readonly_fields(self, request, obj=None):
        """
        Динамически определяет, какие поля "только для чтения".
        """
        if obj and obj.status != Order.OrderStatus.CART:
            # --- Если это ОФОРМЛЕННЫЙ ЗАКАЗ ---
            # Мы разрешаем менять 'status'
            return ('user', 'total_price', 'created_at', 'updated_at', 'get_company')
        else:
            # --- Если это КОРЗИНА (или новый) ---
            # Мы запрещаем менять 'status'
            return ('user', 'status', 'total_price', 'created_at', 'updated_at', 'get_company')
    # ---

    # --- ИЗМЕНЕНИЕ (Goal 4 - Фикс): Динамически меняем "choices" для статуса ---
    def get_form(self, request, obj=None, **kwargs):
        """
        Переопределяем форму, чтобы ограничить 'status'
        """
        form = super().get_form(request, obj, **kwargs)

        # Убедимся, что 'status' есть в полях
        if 'status' not in form.base_fields:
            return form

        if obj and obj.status != Order.OrderStatus.CART:
            # --- Если это ОФОРМЛЕННЫЙ ЗАКАЗ ---
            # Ограничиваем выбор (убираем 'В корзине')
            form.base_fields['status'].choices = [
                (Order.OrderStatus.PENDING, 'В ожидании (Оформлен)'),
                (Order.OrderStatus.COMPLETED, 'Выполнен'),
                (Order.OrderStatus.CANCELLED, 'Отменен'),
            ]
        elif obj is None:
            # --- Если это НОВЫЙ ЗАКАЗ (что мы запретили, но на всякий) ---
            form.base_fields['status'].choices = [
                (Order.OrderStatus.CART, 'В корзине')
            ]

        # Если это 'cart', то 'status' и так readonly,
        # поэтому нам не нужно менять choices

        return form
    # ---

    # --- (get_queryset остается без изменений) ---
    def get_queryset(self, request):
        """
        Не показывать в админке корзины, в которых нет товаров.
        """
        qs = super().get_queryset(request)
        return qs.exclude(status=Order.OrderStatus.CART, items__isnull=True)
    # ---

    @admin.display(description="Компания", ordering='user__company')
    def get_company(self, obj):
        """Получает Компанию из связанного Пользователя"""
        if obj.user and obj.user.company:
            return obj.user.company.name
        return "N/A (Частный)"
    # ---
