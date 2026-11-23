import base64
import hmac
import hashlib
import json
from typing import Tuple
from urllib.parse import unquote
from datetime import datetime, timedelta
import logging  # <--- 1. ДОБАВЛЕН ИМПОРТ

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import User

logger = logging.getLogger(__name__)  # <--- 2. ПОЛУЧАЕМ ЛОГГЕР


class TelegramWebAppDataAuth(BaseAuthentication):
    """
    Кастомный бэкенд аутентификации для проверки данных
    от Telegram Web App (initData).
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('TWA '):
            return None  # Не наш тип аутентификации, пропускаем

        twa_init_data = auth_header.split(' ')[1]

        try:
            is_valid, user_data = self.validate_init_data(twa_init_data)
        except Exception as e:
            logger.warning(f"Ошибка валидации TWA: {e}")  # <--- ЛОГ
            raise AuthenticationFailed(f"Ошибка валидации TWA: {e}")

        if not is_valid:
            logger.warning(
                "Неверные данные TWA: подпись не совпадает.")  # <--- ЛОГ
            raise AuthenticationFailed(
                "Неверные данные TWA: подпись не совпадает.")

        # Данные TWA валидны, ищем пользователя
        try:
            user_id = user_data['id']
            user = User.objects.get(telegram_id=user_id, is_active=True)

        except User.DoesNotExist:
            logger.warning(
                # <--- ЛОГ
                f"TWA Аутентификация: Пользователь {user_id} не найден или неактивен.")
            raise AuthenticationFailed("Пользователь не найден или неактивен.")
        except KeyError:
            logger.error(
                "TWA Аутентификация: Неверный формат данных TWA: отсутствует user id.")  # <--- ЛОГ
            raise AuthenticationFailed(
                "Неверный формат данных TWA: отсутствует user id.")

        # Успех!
        # <--- ЛОГ
        logger.info(
            f"TWA Аутентификация: Успех для {user.username} (TG ID: {user_id})")
        return (user, None)

    def validate_init_data(self, init_data: str) -> Tuple[bool, dict]:
        # ... (вся функция validate_init_data остается без изменений) ...
        try:
            data_dict = dict(param.split('=', 1)
                             for param in init_data.split('&'))
        except ValueError:
            raise ValueError("Неверный формат initData.")
        if 'hash' not in data_dict:
            raise ValueError("В initData отсутствует hash.")
        hash_from_telegram = data_dict.pop('hash')
        data_check_string_parts = []
        for key in sorted(data_dict.keys()):
            data_check_string_parts.append(f"{key}={unquote(data_dict[key])}")
        data_check_string = "\n".join(data_check_string_parts)
        secret_key = hmac.new(
            "WebAppData".encode(),
            settings.TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        local_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        if local_hash != hash_from_telegram:
            return False, {}
        try:
            auth_date_unix = int(json.loads(
                unquote(data_dict['auth_date']))['auth_date'])
            auth_date = datetime.utcfromtimestamp(auth_date_unix)
            if datetime.utcnow() - auth_date > timedelta(hours=1):
                pass
        except Exception:
            pass
        try:
            user_data = json.loads(unquote(data_dict['user']))
        except (KeyError, json.JSONDecodeError):
            raise ValueError(
                "Не удалось извлечь данные пользователя (user) из initData.")
        return True, user_data


class OneCWebhookPrincipal:
    """Сервисный пользователь для аутентификации входящих вебхуков от 1С."""

    is_authenticated = True
    is_active = True
    is_anonymous = False
    username = "1c_webhook"

    def __str__(self):
        return self.username


class OneCBasicAuthentication(BaseAuthentication):
    """
    HTTP Basic Authentication специально для входящих вебхуков от 1С
    (POST /api/v1/webhooks/1c/stocks/ и POST /api/v1/webhooks/1c/customers/).
    """

    def authenticate_header(self, request):
        return 'Basic realm="1C Webhook"'

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization") or ""
        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "basic":
            return None

        expected_user = getattr(settings, "ONE_C_WEBHOOK_USER", "")
        expected_password = getattr(settings, "ONE_C_WEBHOOK_PASSWORD", "")
        if not expected_user or not expected_password:
            logger.error(
                "1C Webhook Auth: ONE_C_WEBHOOK_USER или ONE_C_WEBHOOK_PASSWORD не настроены."
            )
            raise AuthenticationFailed("Учетные данные вебхука не настроены на сервере.")

        try:
            decoded = base64.b64decode(parts[1].strip()).decode("utf-8")
        except Exception:
            try:
                decoded = base64.b64decode(parts[1].strip()).decode("latin-1")
            except Exception as exc:
                logger.warning("1C Webhook Auth: некорректный base64 в Basic-заголовке.")
                raise AuthenticationFailed("Некорректный заголовок Authorization.") from exc

        if ":" not in decoded:
            raise AuthenticationFailed("Некорректный формат Basic-авторизации.")

        username, password = decoded.split(":", 1)
        user_ok = hmac.compare_digest(username, expected_user)
        pass_ok = hmac.compare_digest(password, expected_password)
        if not (user_ok and pass_ok):
            logger.warning("1C Webhook Auth: неверные учетные данные для пользователя '%s'.", username)
            raise AuthenticationFailed("Неверные учетные данные.")

        return (OneCWebhookPrincipal(), "1c_basic")
