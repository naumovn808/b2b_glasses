from django.urls import path, re_path
from . import views, webhooks

# Импорты для Swagger
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# --- Настройка Swagger ---
schema_view = get_schema_view(
    openapi.Info(
        title="B2B Glasses API (v1)",
        default_version='v1',
        description="Документация API v1 для проекта B2B Glasses",
        contact=openapi.Contact(email="contact@example.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
# ---

app_name = "api"

urlpatterns = [
    # --- 1. НАШИ ЭНДПОИНТЫ ---

    # --- СТАРЫЙ ПУТЬ УДАЛЕН ---
    # path('telegram/link/', views.TelegramLinkView.as_view(), name='telegram-link'),

    # --- ДОБАВЛЕН НОВЫЙ ПУТЬ ДЛЯ РЕГИСТРАЦИИ ---
    path('auth/register/', views.BotRegistrationView.as_view(), name='bot-register'),

    # --- ЭТИ ПУТИ ОСТАЮТСЯ ---
    path('auth/set-password/', views.SetPasswordView.as_view(), name='set-password'),
    path('auth/login/', views.LoginView.as_view(), name='api-token-auth'),
    path('auth/me/', views.UserProfileView.as_view(), name='user-profile'),
    path('internal/check-status/', views.CheckUserStatusView.as_view(),
         name='internal-check-status'),

    # --- ВЕБХУКИ ОТ 1С ---
    path('webhooks/1c/stocks/', webhooks.OneCStocksWebhookView.as_view(),
         name='webhook-1c-stocks'),
    path('webhooks/1c/customers/', webhooks.OneCCustomersWebhookView.as_view(),
         name='webhook-1c-customers'),

    # --- 2. НАША ДОКУМЕНТАЦИЯ (SWAGGER) ---
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
]
