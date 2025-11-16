from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    # --- КОРЗИНА ---
    path('cart/', views.CartView.as_view(), name='cart-detail'),
    path('cart/add/', views.AddCartItemView.as_view(), name='cart-add'),
    path('cart/clear/', views.ClearCartView.as_view(), name='cart-clear'),
    path('cart/item/<int:pk>/', views.RemoveCartItemView.as_view(),
         name='cart-remove-item'),
    path('cart/checkout/', views.CheckoutView.as_view(), name='cart-checkout'),

    # --- НОВЫЙ ПУТЬ ---
    # GET (Получить историю заказов)
    path('history/', views.OrderHistoryView.as_view(), name='order-history'),
]
