from django.contrib import admin
from .models import Order, OrderItem, CustomOrder
from users.models import Company


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'quantity', 'price_at_order', 'total_price')
    readonly_fields = ('product', 'quantity', 'price_at_order', 'total_price')
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'get_company', 'status', 'total_price', 'created_at'
    )
    list_filter = ('status', 'user__company', 'created_at')
    search_fields = ('id', 'user__username',
                     'user__phone_number', 'user__company__name')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Детали Заказа', {
            'fields': ('status', 'total_price', 'created_at', 'updated_at')
        }),
        ('Контрагент', {
            'fields': ('user', 'get_company')
        }),
    )

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != Order.OrderStatus.CART:
            return ('user', 'total_price', 'created_at', 'updated_at', 'get_company')
        else:
            return ('user', 'status', 'total_price', 'created_at', 'updated_at', 'get_company')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(status=Order.OrderStatus.CART, items__isnull=True)

    @admin.display(description="Компания", ordering='user__company')
    def get_company(self, obj):
        if obj.user and obj.user.company:
            return obj.user.company.name
        return "N/A"


# --- НОВАЯ АДМИНКА ДЛЯ CUSTOM ORDER ---
@admin.register(CustomOrder)
class CustomOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'series', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__phone_number',
                     'design', 'photochrom')

    # Поля, которые менеджер не должен менять (они пришли от клиента)
    readonly_fields = (
        'user', 'series', 'sph', 'cyl', 'dia',
        'design', 'photochrom', 'created_at'
    )

    fieldsets = (
        ('Статус заявки', {
            'fields': ('status', 'comment')
        }),
        ('Параметры Линз', {
            'fields': (
                ('sph', 'cyl', 'dia'),
                'series',
                'design',
                'photochrom'
            )
        }),
        ('Клиент', {
            'fields': ('user', 'created_at')
        }),
    )
