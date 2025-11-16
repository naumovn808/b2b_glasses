from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Классическая схема:
    # Все, что начинается с /api/v1/,
    # будет обрабатываться файлом 'api.urls'
    path('api/v1/', include('api.urls', namespace='api')),

    path('api/v1/catalog/', include('catalog.urls', namespace='catalog')),

    path('api/v1/orders/', include('orders.urls', namespace='orders')),
]
