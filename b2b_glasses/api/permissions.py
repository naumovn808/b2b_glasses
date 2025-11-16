from rest_framework.permissions import BasePermission
from django.conf import settings


class IsBot(BasePermission):
    """
    Разрешение, которое проверяет, что запрос пришел
    от нашего бота (по секретному ключу в заголовке).
    """

    def has_permission(self, request, view):
        # Получаем заголовок 'X-Bot-Token'
        bot_token = request.headers.get('X-Bot-Token')

        # Проверяем, совпадает ли он с нашим секретом из settings.py
        if not bot_token or bot_token != settings.BOT_API_SECRET:
            return False
        return True
