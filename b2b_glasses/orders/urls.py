from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    # --- КОРЗИНА ---
    path('cart/', views.CartView.as_view(), name='cart-detail'),
    path('cart/add/', views.AddCartItemView.as_view(), name='cart-add'),
    path('cart/clear/', views.ClearCartView.as_view(), name='cart-clear'),
    path('cart/checkout/', views.CheckoutView.as_view(), name='cart-checkout'),

    # Управление позициями
    path('cart/items/<int:pk>/', views.RemoveCartItemView.as_view(),
         name='cart-remove-item'),
    path('cart/items/<int:pk>/update/',
         views.UpdateCartItemView.as_view(), name='cart-update-item'),

    # История
    path('history/', views.OrderHistoryView.as_view(), name='order-history'),

    # --- НОВЫЙ ПУТЬ: Индивидуальные заказы ---
    path('custom/create/', views.CreateCustomOrderView.as_view(),
         name='custom-order-create'),
]
