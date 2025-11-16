import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.core.management import call_command

# Получаем логгер 'catalog', который мы настроили в settings.py
logger = logging.getLogger(__name__)

# --- Константы ---
DEFAULT_INTERVAL_MINUTES = 30
RETRY_INTERVAL_MINUTES = 5
JOB_ID = 'import_1c_xml_job'

# --- ИЗМЕНЕНИЕ:
# Создаем scheduler здесь, как ГЛОБАЛЬНЫЙ объект, один раз
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def scheduled_import_job():
    """
    Работа, которую мы будем выполнять по расписанию.
    Она использует ГЛОБАЛЬНЫЙ 'scheduler' для самомодификации.
    """
    # Аргумент (scheduler) больше не нужен

    logger.info("--- [APScheduler] Запуск планового импорта 1С... ---")
    try:
        # Вызываем нашу команду
        call_command('import_1c_xml')

        logger.info(
            "--- [APScheduler] Плановый импорт 1С успешно завершен. ---")

        # --- ИЗМЕНЕНИЕ: Используем ГЛОБАЛЬНЫЙ scheduler ---
        current_job = scheduler.get_job(JOB_ID)

        if (current_job and
                current_job.trigger.interval.total_seconds() != DEFAULT_INTERVAL_MINUTES * 60):

            logger.warning(
                f"--- [APScheduler] Успех! Возвращаю интервал на {DEFAULT_INTERVAL_MINUTES} минут. ---")

            # Используем ГЛОБАЛЬНЫЙ scheduler
            scheduler.modify_job(
                JOB_ID,
                trigger='interval',
                minutes=DEFAULT_INTERVAL_MINUTES
            )

    except Exception as e:
        logger.error("--- [APScheduler] ПЛАНОВЫЙ ИМПОРТ 1С ПРОВАЛИЛСЯ! ---")
        logger.error(e, exc_info=True)

        logger.warning(
            f"--- [APScheduler] Ошибка! Следующая попытка через {RETRY_INTERVAL_MINUTES} минут. ---")

        # --- ИЗМЕНЕНИЕ: Используем ГЛОБАЛЬНЫЙ scheduler ---
        scheduler.modify_job(
            JOB_ID,
            trigger='interval',
            minutes=RETRY_INTERVAL_MINUTES
        )


def start():
    """
    Главная функция запуска планировщика.
    """
    # --- ИЗМЕНЕНИЕ: scheduler уже создан и настроен выше ---

    # Добавляем нашу работу в расписание
    scheduler.add_job(
        scheduled_import_job,         # <--- Функция без аргументов
        trigger='interval',
        minutes=DEFAULT_INTERVAL_MINUTES,
        id=JOB_ID,

        # args=[scheduler],  <--- ЭТА СТРОКА УДАЛЕНА (ОНА ВЫЗЫВАЛА ОШИБКУ)

        replace_existing=True,
        misfire_grace_time=60*5
    )

    logger.info(
        f"--- [APScheduler] Планировщик запущен. Задание '{JOB_ID}' будет выполняться каждые {DEFAULT_INTERVAL_MINUTES} минут. ---")

    # --- ВАЖНОЕ ИЗМЕНЕНИЕ: Защита от двойного запуска ---
    # В режиме разработки (runserver) Django Autoreloader запускает
    # .ready() дважды. Эта проверка не даст запустить scheduler второй раз.
    try:
        if not scheduler.running:
            scheduler.start()
        else:
            logger.warning(
                "--- [APScheduler] Планировщик уже запущен (пропуск из-за autoreload). ---")
    except Exception as e:
        logger.error(
            f"--- [APScheduler] Не удалось запустить планировщик: {e}")
        # Очищаем задачи, если что-то пошло не так при запуске
        scheduler.shutdown()
