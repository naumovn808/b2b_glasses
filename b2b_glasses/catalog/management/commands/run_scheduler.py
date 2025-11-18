from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
import time
import logging

# Импортируем функцию настройки ПЕРИОДИЧЕСКИХ задач
# (предполагаю, она у вас в catalog/scheduler.py)
from catalog.scheduler import scheduled_import_job, DEFAULT_INTERVAL_MINUTES, JOB_ID

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Запускает единый процесс планировщика для всего проекта"

    def handle(self, *args, **options):
        logger.info("--- Инициализация основного планировщика ---")
        
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # 1. Регистрируем ПЕРИОДИЧЕСКУЮ задачу (Импорт 1С)
        scheduler.add_job(
            scheduled_import_job,
            trigger='interval',
            minutes=DEFAULT_INTERVAL_MINUTES,
            id=JOB_ID,
            replace_existing=True,
            misfire_grace_time=60*10
        )
        logger.info(f"Задача '{JOB_ID}' добавлена в расписание.")

        # 2. Запускаем планировщик
        # Он начнет выполнять и периодические задачи, 
        # И те "одноразовые" задачи FTP, которые веб-сайт положит в БД.
        scheduler.start()
        logger.info("--- Планировщик ЗАПУЩЕН и ждет задачи ---")

        try:
            # Бесконечный цикл, чтобы Docker-контейнер не закрылся
            while True:
                time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Остановка планировщика...")
            scheduler.shutdown()