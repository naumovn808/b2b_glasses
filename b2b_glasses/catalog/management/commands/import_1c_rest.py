import logging

from django.core.management.base import BaseCommand, CommandError

from api.one_c_client import OneCAPIError, OneCClient
from catalog.one_c_sync import sync_frames_from_1c, sync_lenses_from_1c
from users.one_c_sync import sync_customers_from_1c

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Синхронизирует оправы, линзы и контрагентов из REST API 1С."

    def add_arguments(self, parser):
        parser.add_argument(
            "--frames-only",
            action="store_true",
            help="Синхронизировать только оправы.",
        )
        parser.add_argument(
            "--lenses-only",
            action="store_true",
            help="Синхронизировать только линзы.",
        )
        parser.add_argument(
            "--customers-only",
            action="store_true",
            help="Синхронизировать только контрагентов.",
        )
        parser.add_argument(
            "--skip-customers",
            action="store_true",
            help="Пропустить синхронизацию контрагентов.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Размер страницы при запросе каталога (по умолчанию ONE_C_PAGE_LIMIT).",
        )

    def handle(self, *args, **options):
        frames_only = options["frames_only"]
        lenses_only = options["lenses_only"]
        customers_only = options["customers_only"]
        skip_customers = options["skip_customers"]
        limit = options["limit"]

        selective = frames_only or lenses_only or customers_only
        run_frames = frames_only or not selective
        run_lenses = lenses_only or not selective
        run_customers = customers_only or (not selective and not skip_customers)

        client = OneCClient()

        try:
            if run_frames:
                self.stdout.write("Синхронизация оправ из 1С...")
                res = sync_frames_from_1c(client=client, limit=limit)
                self.stdout.write(self.style.SUCCESS(f"Оправы: {res}"))

            if run_lenses:
                self.stdout.write("Синхронизация линз из 1С...")
                res = sync_lenses_from_1c(client=client, limit=limit)
                self.stdout.write(self.style.SUCCESS(f"Линзы: {res}"))

            if run_customers:
                self.stdout.write("Синхронизация контрагентов из 1С...")
                res = sync_customers_from_1c(client=client)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Контрагенты: обработано {res['processed']}"
                    )
                )
        except OneCAPIError as exc:
            logger.error("[import_1c_rest] Ошибка API 1С: %s", exc)
            raise CommandError(f"Ошибка API 1С: {exc}") from exc
        except Exception as exc:
            logger.exception("[import_1c_rest] Непредвиденная ошибка синхронизации")
            raise CommandError(f"Ошибка синхронизации с 1С: {exc}") from exc

