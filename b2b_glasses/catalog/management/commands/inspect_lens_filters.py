from django.core.management.base import BaseCommand
from django.db.models import Count
from catalog.models import Lens, LensSeries
import json


class Command(BaseCommand):
    help = 'Показывает все уникальные значения фильтров для Линз из БД.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            '--- [Анализ Фильтров Линз из Базы Данных] ---'))

        # 1. Получаем все Серии (Бренды) Линз
        # (Это отдельная таблица LensSeries)
        try:
            series = LensSeries.objects.annotate(
                lens_count=Count('lens')
            ).order_by('name')

            self.stdout.write(self.style.WARNING(
                f'\n[ 1. Серии Линз (найдено {series.count()}) ]'))
            if not series.exists():
                self.stdout.write('  (Пусто)')
            else:
                for s in series:
                    self.stdout.write(
                        f'  - "{s.name}" (товаров: {s.lens_count})')
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при получении Серий: {e}'))

        # 2. Получаем все уникальные Сферы (SPH)
        # (Это поле 'sph' в основной модели 'Lens')
        try:
            # .values_list('sph', flat=True) - взять только значения SPH
            # .distinct() - только уникальные
            # .order_by('sph') - отсортировать
            sph_values = Lens.objects.values_list(
                'sph', flat=True).distinct().order_by('sph')

            self.stdout.write(self.style.WARNING(
                f'\n[ 2. Уникальные Сферы (SPH) (найдено {sph_values.count()}) ]'))
            if not sph_values:
                self.stdout.write('  (Пусто)')
            else:
                # Печатаем в одну строку, чтобы было компактно
                self.stdout.write(
                    ", ".join([str(val) for val in sph_values])
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при получении SPH: {e}'))

        # 3. Получаем все уникальные Цилиндры (CYL)
        try:
            cyl_values = Lens.objects.values_list(
                'cyl', flat=True).distinct().order_by('cyl')

            self.stdout.write(self.style.WARNING(
                f'\n[ 3. Уникальные Цилиндры (CYL) (найдено {cyl_values.count()}) ]'))
            if not cyl_values:
                self.stdout.write('  (Пусто)')
            else:
                self.stdout.write(
                    ", ".join([str(val) for val in cyl_values])
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при получении CYL: {e}'))

        # 4. Получаем все уникальные Диаметры (DIA)
        try:
            dia_values = Lens.objects.values_list(
                'dia', flat=True).distinct().order_by('dia')

            self.stdout.write(self.style.WARNING(
                f'\n[ 4. Уникальные Диаметры (DIA) (найдено {dia_values.count()}) ]'))
            if not dia_values:
                self.stdout.write('  (Пусто)')
            else:
                self.stdout.write(
                    ", ".join([str(val) for val in dia_values])
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при получении DIA: {e}'))

        self.stdout.write(self.style.SUCCESS('\n--- [Анализ завершен] ---'))
