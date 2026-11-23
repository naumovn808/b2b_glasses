import os
import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.management import call_command

logger = logging.getLogger(__name__)

JOB_ID = "smart_1c_import"
TIMESTAMP_FILE = os.path.join(settings.BASE_DIR, "last_import_success.txt")
SUCCESS_INTERVAL_MINUTES = 30


def get_last_success_time():
    if not os.path.exists(TIMESTAMP_FILE):
        return None
    try:
        with open(TIMESTAMP_FILE, "r") as f:
            return timezone.datetime.fromisoformat(f.read().strip())
    except:
        return None


def set_last_success_time(dt):
    with open(TIMESTAMP_FILE, "w") as f:
        f.write(dt.isoformat())


def smart_import_job():
    """
    Запускается планировщиком каждые 5 минут.
    """
    now = timezone.now()
    last_success = get_last_success_time()

    # 1. Если с последнего успеха прошло меньше 30 минут — ничего не делаем
    if last_success:
        if (now - last_success) < timedelta(minutes=SUCCESS_INTERVAL_MINUTES):
            return

    # 2. Пытаемся запустить импорт
    try:
        logger.info("[Smart Import] Запуск команды REST-синхронизации с 1С...")

        call_command("import_1c_rest")

        # 3. Если команда выполнилась без ошибок — обновляем время успеха
        logger.info("[Smart Import] Импорт завершен успешно.")
        set_last_success_time(now)

    except Exception as e:
        # 4. Если ошибка — логгируем и НЕ обновляем время.
        # В следующий тик (через 5 минут) условие времени снова пустит нас сюда.
        logger.error(f"[Smart Import] Ошибка при импорте: {e}")
