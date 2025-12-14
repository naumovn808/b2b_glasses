from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # CKEditor (для загрузки картинок)
    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('api/v1/', include('api.urls', namespace='api')),
    path('api/v1/catalog/', include('catalog.urls', namespace='catalog')),
    path('api/v1/orders/', include('orders.urls', namespace='orders')),

    # --- НОВОЕ ПРИЛОЖЕНИЕ ---
    path('api/v1/content/', include('content.urls', namespace='content')),
]

# Раздача медиа-файлов в режиме DEBUG (чтобы картинки открывались локально)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
