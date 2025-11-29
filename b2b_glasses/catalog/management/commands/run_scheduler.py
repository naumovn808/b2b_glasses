from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.conf import settings
import time
import logging
from catalog.scheduler import smart_import_job, JOB_ID

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Запускает планировщик задач"

    def handle(self, *args, **options):
        # Обязательно передаем timezone
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Запускаем нашу функцию каждые 5 минут
        scheduler.add_job(
            smart_import_job,
            trigger='interval',
            minutes=5,
            id=JOB_ID,
            replace_existing=True,
            misfire_grace_time=300
        )

        scheduler.start()
        logger.info("Планировщик запущен. Проверка импорта каждые 5 минут.")

        try:
            while True:
                time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
