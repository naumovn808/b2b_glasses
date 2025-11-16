import os
import re
import xml.etree.ElementTree as ET
import ftplib
from decimal import Decimal, InvalidOperation
from pathlib import Path
import logging
import uuid
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from catalog.models import (
    Brand, FrameMaterial, FrameShape, FrameType, FrameGender,
    FrameAgeGroup, Frame, LensSeries, Lens
)

logger = logging.getLogger(__name__)


NS = {'cml': 'urn:1C.ru:commerceml_2'}
FILES_TO_DOWNLOAD = [
    'import0_1.xml', 'offers0_1.xml', 'import1_1.xml', 'offers1_1.xml'
]
REMOTE_PATH = "/Выгрузка/webdata"
LENS_SERIES_RE = re.compile(r'^(.*?)\s*\(')
LENS_SPH_RE = re.compile(r'\(\s*([+-]\d+\.\d+)')
LENS_CYL_RE = re.compile(r'cyl\s*([+-]\d+\.\d+)')
LENS_DIA_RE = re.compile(r'D\.(\d+)')


class Command(BaseCommand):
    help = 'Подключается к FTP, скачивает 4 XML-файла и импортирует их в БД.'

    def handle(self, *args, **options):

        self.skipped_frames = 0
        self.skipped_lenses = 0

        self.current_run_id = uuid.uuid4()
        logger.info(f"--- [RUN ID: {self.current_run_id}] ---")

        temp_dir = Path(settings.BASE_DIR) / "temp_xml"
        try:
            os.makedirs(temp_dir, exist_ok=True)
            logger.info(f'Создана временная папка: {temp_dir}')
        except Exception as e:
            logger.critical(f'Не удалось создать временную папку: {e}')
            raise CommandError(f'Не удалось создать временную папку: {e}')

        try:
            logger.info(
                f'Подключаюсь к FTP: {settings.FTP_HOST}:{settings.FTP_PORT} (encoding=utf-8)...')
            with ftplib.FTP(encoding='utf-8') as ftp:
                ftp.connect(settings.FTP_HOST, settings.FTP_PORT)
                ftp.login(settings.FTP_USER, settings.FTP_PASS)
                ftp.sendcmd("OPTS UTF8 ON")
                ftp.encoding = "utf-8"
                ftp.set_pasv(True)
                logger.info('Успешно подключен к FTP (UTF-8).')
                logger.info(f'Перехожу в папку: {REMOTE_PATH}')
                ftp.cwd(REMOTE_PATH)
                # --- ИЗМЕНЕНИЕ: Уточнено сообщение ---
                logger.info(f'Скачиваю {len(FILES_TO_DOWNLOAD)} файла...')
                downloaded_count = 0

                for filename in tqdm(FILES_TO_DOWNLOAD, desc="Скачивание XML"):
                    local_path = os.path.join(temp_dir, filename)
                    try:
                        with open(local_path, 'wb') as f:
                            ftp.retrbinary(f'RETR {filename}', f.write)

                        downloaded_count += 1
                    except Exception as e:
                        # --- ИЗМЕНЕНИЕ: Критическая ошибка ---
                        # Если ОДИН файл не скачался (не найден, нет прав),
                        # нет смысла продолжать.
                        logger.critical(
                            f'  [КРИТИЧЕСКАЯ ОШИБКА] Не удалось скачать {filename}: {e}')
                        logger.critical(
                            'Процесс импорта будет остановлен. База данных НЕ будет затронута.')
                        # Вызываем CommandError, чтобы остановить выполнение handle()
                        raise CommandError(f'Ошибка скачивания файла: {e}')
                        # --- КОНЕЦ ИЗМЕНЕНИЯ ---

                # --- ИЗМЕНЕНИЕ: Более строгая проверка ---
                # Эта проверка гарантирует, что скачаны ВСЕ файлы.
                # (Хотя 'except' выше уже должен был поймать 550 'No such file')
                if downloaded_count < len(FILES_TO_DOWNLOAD):
                    logger.critical(
                        f'ОШИБКА: Скачано {downloaded_count} из {len(FILES_TO_DOWNLOAD)} необходимых файлов.')
                    logger.critical(
                        'Процесс импорта будет остановлен. База данных НЕ будет затронута.')
                    raise CommandError('Не все файлы были успешно скачаны.')

                logger.info(f'Успешно скачано {downloaded_count} файла.')
                # --- КОНЕЦ ИЗМЕНЕНИЯ ---

        except ftplib.error_perm as e:
            logger.critical(
                f'Ошибка FTP (Папка "{REMOTE_PATH}" не найдена?): {e}')
            raise CommandError(f'Ошибка FTP: {e}')
        except Exception as e:
            # --- ИЗМЕНЕНИЕ: Обработка CommandError, который мы вызвали ---
            if isinstance(e, CommandError):
                raise  # Просто пробрасываем нашу ошибку дальше

            logger.critical(f'Ошибка FTP (адрес/порт?): {e}')
            raise CommandError(f'Ошибка FTP: {e}')
            # --- КОНЕЦ ИЗМЕНЕНИЯ ---

        xml_path = str(temp_dir)

        self.file_frames_import = os.path.join(xml_path, 'import0_1.xml')
        self.file_frames_offers = os.path.join(xml_path, 'offers0_1.xml')
        self.file_lenses_import = os.path.join(xml_path, 'import1_1.xml')
        self.file_lenses_offers = os.path.join(xml_path, 'offers1_1.xml')

        # --- НОВЫЙ БЛОК: "PRE-FLIGHT" ПРОВЕРКА ФАЙЛОВ ---
        # Проверяем, что все 4 файла существуют и являются валидным XML
        # ДО того, как мы начнем транзакцию с БД.

        all_local_files_to_check = [
            self.file_frames_import,
            self.file_frames_offers,
            self.file_lenses_import,
            self.file_lenses_offers
        ]

        logger.info('Запуск "Pre-flight" проверки скачанных XML-файлов...')
        try:
            current_check_file = ""  # Для логирования ошибки
            for f_path in tqdm(all_local_files_to_check, desc="Проверка XML (Pre-flight)"):
                current_check_file = f_path
                # 1. Проверка на существование
                if not os.path.exists(f_path):
                    logger.critical(
                        f'Файл {f_path} отсутствует после скачивания.')
                    raise FileNotFoundError(f'Файл {f_path} отсутствует.')

                # 2. Проверка на корректность XML (пытаемся распарсить корень)
                ET.parse(f_path)

            logger.info('...[OK] Все XML-файлы корректны и готовы к импорту.')

        except ET.ParseError as e:
            logger.critical(
                f'Ошибка парсинга XML (файл поврежден?): {current_check_file} - {e}')
            logger.critical(
                'Импорт остановлен. База данных НЕ будет затронута.')
            raise CommandError(f'Ошибка парсинга XML: {e}')
        except FileNotFoundError as e:
            logger.critical(f'Ошибка "Pre-flight": Файл не найден. {e}')
            logger.critical(
                'Импорт остановлен. База данных НЕ будет затронута.')
            raise CommandError(f'Ошибка "Pre-flight": Файл не найден. {e}')
        except Exception as e:
            logger.critical(
                f'Неизвестная ошибка при "Pre-flight" проверке: {e}')
            raise CommandError(f'Ошибка проверки файлов: {e}')
        # --- КОНЕЦ НОВОГО БЛОКА ---

        logger.info('--- Начало импорта каталога 1C ---')

        try:
            deleted_frames = 0
            deleted_lenses = 0

            with transaction.atomic():
                logger.info('Шаг 1: Импорт Оправ (import0_1.xml)...')
                self.frame_id_map = self._import_frames()

                logger.info(
                    f'Обработано {len(self.frame_id_map)} Оправ.')
                if self.skipped_frames > 0:
                    logger.warning(
                        f'Пропущено {self.skipped_frames} Оправ (отсутствует Ид).')

                logger.info('Шаг 2: Импорт Линз (import1_1.xml)...')
                self.lens_id_map = self._import_lenses()
                logger.info(
                    f'Обработано {len(self.lens_id_map)} Линз.')
                if self.skipped_lenses > 0:
                    logger.warning(
                        f'Пропущено {self.skipped_lenses} Линз (ошибки парсинга).')

                logger.info(
                    'Шаг 3: Обновление Цен/Остатков Оправ (offers0_1.xml)...')
                count_f = self._update_offers(
                    self.file_frames_offers, self.frame_id_map, Frame, step_num=3)
                logger.info(f'Обновлено {count_f} Оправ.')

                logger.info(
                    'Шаг 4: Обновление Цен/Остатков Линз (offers1_1.xml)...')
                count_l = self._update_offers(
                    self.file_lenses_offers, self.lens_id_map, Lens, step_num=4)
                logger.info(f'Обновлено {count_l} Линз.')

                logger.info(
                    '--- Шаг 5: Атомарная очистка (Удаление старых товаров) ---')

                logger.warning(
                    f"  ...[!] Начинаю УДАЛЕНИЕ старых записей... ОЖИДАЙТЕ...")
                # --- ИЗМЕНЕНИЕ: Вложенная транзакция для очистки ---
                # Это гарантирует, что если очистка не удастся,
                # то импорт (Шаги 1-4) также откатится.
               # ... (Начало Шага 5) ...
                with transaction.atomic():
                    # deleted_frames_qs ТЕПЕРЬ ЯВЛЯЕТСЯ ЧИСЛОМ (int)
                    deleted_frames_qs, _ = Frame.objects.exclude(
                        run_id=self.current_run_id).delete()

                    # deleted_lenses_qs ТЕПЕРЬ ЯВЛЯЕТСЯ ЧИСЛОМ (int)
                    deleted_lenses_qs, _ = Lens.objects.exclude(
                        run_id=self.current_run_id).delete()

                    # --- ИСПРАВЛЕНИЕ ---
                    # Просто присваиваем это число.
                    # .get() здесь не нужен.
                    deleted_frames = deleted_frames_qs
                    deleted_lenses = deleted_lenses_qs
                    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

                logger.info(
                    f"  ...[OK] УДАЛЕНИЕ старых записей завершено.")

            # --- ИЗМЕНЕНИЕ: Логирование вынесено из транзакции ---
            # Эти сообщения появятся, только если ВСЯ
            # внешняя транзакция (Шаги 1-5) успешно закоммитилась.
            logger.info(
                f'Очистка завершена. Удалено {deleted_frames} старых Оправ.')
            logger.info(
                f'Очистка завершена. Удалено {deleted_lenses} старых Линз.')

            logger.info(
                f'--- Импорт (RUN ID: {self.current_run_id}) успешно завершен! ---')

        except FileNotFoundError as e:
            # Эти ошибки теперь маловероятны из-за Pre-flight проверки,
            # но мы оставляем их как дополнительный уровень защиты.
            logger.critical(f'Ошибка: Файл не найден. {e}')
            raise CommandError(f'Ошибка: Файл не найден. {e}')
        except ET.ParseError as e:
            # Аналогично, маловероятно, но оставляем.
            logger.critical(f'Ошибка парсинга XML (файл поврежден?): {e}')
            raise CommandError(f'Ошибка парсинга XML: {e}')
        except Exception as e:
            logger.critical(
                f'Произошла неизвестная ошибка импорта (транзакция отменена): {e}', exc_info=True)
            raise CommandError(f'Импорт прерван из-за ошибки: {e}')

    # ... (Остальные функции _find_text, _import_frames, _import_lenses,
    # _parse_lens_name, _update_offers остаются без изменений) ...

    def _find_text(self, element, path, default=''):
        # ... (код без изменений) ...
        tag = element.find(path, NS)
        if tag is not None and tag.text is not None:
            return tag.text.strip()
        return default

    def _import_frames(self):
        # ... (код без изменений) ...
        classifier = {}
        try:
            tree = ET.parse(self.file_frames_import)
            root = tree.getroot()
        except FileNotFoundError:
            logger.error(
                f"ОШИБКА в _import_frames: не найден {self.file_frames_import}")
            raise

        classifier_tag = root.find('cml:Классификатор', NS)
        if classifier_tag is None:
            logger.warning('  ! Не найден <Классификатор> в Оправах.')
            return {}

        for prop in classifier_tag.findall('cml:Свойства/cml:Свойство', NS):
            prop_id = self._find_text(prop, 'cml:Ид')
            prop_name = self._find_text(prop, 'cml:Наименование')
            if prop_id and prop_name:
                classifier[prop_id] = prop_name
        logger.info(
            f'  ...Классификатор Оправ загружен (Найдено {len(classifier)} свойств).')

        logger.info('  ...Кеширование справочников...')
        brands_cache = {b.name: b for b in Brand.objects.all()}
        materials_cache = {m.name: m for m in FrameMaterial.objects.all()}
        shapes_cache = {s.name: s for s in FrameShape.objects.all()}
        types_cache = {t.name: t for t in FrameType.objects.all()}
        genders_cache = {g.name: g for g in FrameGender.objects.all()}
        ages_cache = {a.name: a for a in FrameAgeGroup.objects.all()}
        logger.info('  ...Кеширование завершено.')

        id_map = {}
        catalog_tag = root.find('cml:Каталог', NS)
        if catalog_tag is None:
            logger.warning('  ! Не найден <Каталог> в Оправах.')
            return {}

        product_nodes = catalog_tag.findall('cml:Товары/cml:Товар', NS)
        logger.info(
            f"  Найдено {len(product_nodes)} товаров (Оправ). Начинаю обработку...")

        for product in tqdm(product_nodes, desc="  Шаг 1 (Оправы)"):
            id_1c = self._find_text(product, 'cml:Ид')
            if not id_1c:

                self.skipped_frames += 1
                continue

            data = {

                'name': self._find_text(product, 'cml:Наименование'),
                'sku': self._find_text(product, 'cml:Артикул'),
                'barcode': self._find_text(product, 'cml:Штрихкод'),
                'run_id': self.current_run_id
            }

            brand_tag = product.find('cml:Изготовитель', NS)
            if brand_tag is not None:
                brand_name = self._find_text(brand_tag, 'cml:Наименование')
                if brand_name:
                    brand = brands_cache.get(brand_name)
                    if not brand:
                        brand = Brand.objects.create(name=brand_name)
                        brands_cache[brand_name] = brand
                    data['brand'] = brand

            props_list = product.find('cml:ЗначенияСвойств', NS)
            if props_list is not None:
                for prop in props_list.findall('cml:ЗначенияСвойства', NS):

                    prop_id = self._find_text(prop, 'cml:Ид')
                    prop_val = self._find_text(prop, 'cml:Значение')
                    prop_name = classifier.get(prop_id)
                    if not prop_name or not prop_val:
                        continue
                    try:
                        prop_val_clean = prop_val.replace(',', '.')
                        if prop_name == 'Пол':
                            gender = genders_cache.get(prop_val)
                            if not gender:
                                gender = FrameGender.objects.create(
                                    name=prop_val)
                                genders_cache[prop_val] = gender
                            data['gender'] = gender

                        elif prop_name == 'Возраст':
                            age = ages_cache.get(prop_val)
                            if not age:
                                age = FrameAgeGroup.objects.create(
                                    name=prop_val)
                                ages_cache[prop_val] = age
                            data['age_group'] = age

                        elif prop_name == 'Материал':
                            mat = materials_cache.get(prop_val)
                            if not mat:
                                mat = FrameMaterial.objects.create(
                                    name=prop_val)
                                materials_cache[prop_val] = mat
                            data['material'] = mat
                        elif prop_name == 'Форма':
                            shape = shapes_cache.get(prop_val)
                            if not shape:
                                shape = FrameShape.objects.create(
                                    name=prop_val)
                                shapes_cache[prop_val] = shape
                            data['shape'] = shape
                        elif prop_name == 'Тип':
                            ftype = types_cache.get(prop_val)
                            if not ftype:
                                ftype = FrameType.objects.create(name=prop_val)
                                types_cache[prop_val] = ftype
                            data['type'] = ftype
                        elif prop_name == 'Цвет':
                            data['color_code'] = prop_val
                        elif prop_name == 'Оригинальный цвет производителя':
                            data['color_name'] = prop_val
                        elif prop_name == 'Размер А':
                            data['size_a'] = Decimal(prop_val_clean)
                        elif prop_name == 'Размер B':
                            data['size_b'] = Decimal(prop_val_clean)
                        elif prop_name == 'Размер D':
                            data['size_d'] = Decimal(prop_val_clean)
                        elif prop_name == 'Размер Заушника':
                            data['size_temple'] = Decimal(prop_val_clean)
                    except (ValueError, TypeError, InvalidOperation):

                        continue

            frame_obj, created = Frame.objects.update_or_create(
                id_1c=id_1c,
                defaults=data
            )
            id_map[id_1c] = frame_obj.id

        return id_map

    def _import_lenses(self):
        # ... (код без изменений) ...
        id_map = {}
        try:
            tree = ET.parse(self.file_lenses_import)
            root = tree.getroot()
        except FileNotFoundError:
            logger.error(
                f"ОШИБКА в _import_lenses: не найден {self.file_lenses_import}")
            raise

        catalog_tag = root.find('cml:Каталог', NS)
        if catalog_tag is None:
            logger.warning('  ! Не найден <Каталог> в Линзах.')
            return {}

        logger.info('  ...Кеширование Серий Линз...')
        series_cache = {s.name: s for s in LensSeries.objects.all()}
        logger.info('  ...Кеширование завершено.')

        product_nodes = catalog_tag.findall('cml:Товары/cml:Товар', NS)
        logger.info(
            f"  Найдено {len(product_nodes)} товаров (Линз). Начинаю обработку...")

        for product in tqdm(product_nodes, desc="  Шаг 2 (Линзы)"):
            id_1c = self._find_text(product, 'cml:Ид')
            full_name = self._find_text(product, 'cml:Наименование')

            if not id_1c or not full_name:
                self.skipped_lenses += 1
                continue

            series_name, sph, cyl, dia = self._parse_lens_name(full_name)

            if not series_name:
                self.skipped_lenses += 1
                continue

            series = series_cache.get(series_name)
            if not series:
                series = LensSeries.objects.create(name=series_name)
                series_cache[series_name] = series

            lens_obj, created = Lens.objects.update_or_create(
                id_1c=id_1c,
                defaults={
                    'series': series,
                    'sph': sph,
                    'cyl': cyl,
                    'dia': dia,
                    'run_id': self.current_run_id
                }
            )
            id_map[id_1c] = lens_obj.id

        return id_map

    def _parse_lens_name(self, name):
        # ... (код без изменений) ...
        try:
            series_match = LENS_SERIES_RE.search(name)
            sph_match = LENS_SPH_RE.search(name)
            dia_match = LENS_DIA_RE.search(name)
            if not all([series_match, sph_match, dia_match]):
                return None, None, None, None
            series = series_match.group(1).strip()
            sph = sph_match.group(1)
            dia = dia_match.group(1)
            cyl_match = LENS_CYL_RE.search(name)
            cyl = cyl_match.group(1) if cyl_match else "0.00"
            return series, Decimal(sph), Decimal(cyl), int(dia)
        except (AttributeError, InvalidOperation, ValueError):
            return None, None, None, None

    BATCH_SIZE = 100

    def _update_offers(self, filepath, id_map, model_class, step_num):
        # ... (код без изменений) ...
        count = 0
        objects_to_update = []
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
        except FileNotFoundError:
            logger.error(f"ОШИБКА в _update_offers: не найден {filepath}")
            raise

        offers_pack = root.find('cml:ПакетПредложений', NS)
        if offers_pack is None:
            logger.warning(f'  ! Не найден <ПакетПредложений> в {filepath}')
            return 0

        offer_nodes = offers_pack.findall(
            'cml:Предложения/cml:Предложение', NS)
        logger.info(
            f"  Найдено {len(offer_nodes)} предложений. Начинаю Python-обработку...")

        for offer in tqdm(offer_nodes, desc=f"  Шаг {step_num} (Python-обработка)"):
            id_1c = self._find_text(offer, 'cml:Ид')
            obj_db_id = id_map.get(id_1c)

            if not obj_db_id:
                continue

            try:
                price = self._find_text(
                    offer, 'cml:Цены/cml:Цена/cml:ЦенаЗаЕдиницу')
                stock = self._find_text(offer, 'cml:Количество')

                if price == '' or stock == '':
                    raise ValueError("Тег цены или количества пустой")

                price_decimal = Decimal(price)
                stock_int = int(stock)

                obj = model_class(
                    id=obj_db_id,
                    price=price_decimal,
                    stock=stock_int
                )
                objects_to_update.append(obj)
                count += 1

            except (InvalidOperation, TypeError, ValueError) as e:
                continue

        if objects_to_update:
            logger.info(
                f"  ...[OK] Python-обработка {len(objects_to_update)} предложений завершена.")

            total_batches = (len(objects_to_update) +
                             self.BATCH_SIZE - 1) // self.BATCH_SIZE

            logger.warning(
                f"  ...[!] Начинаю BATCH-ЗАПИСЬ в БД ({total_batches} партий по {self.BATCH_SIZE} шт.). ОЖИДАЙТЕ...")

            batch_progress = tqdm(
                range(0, len(objects_to_update), self.BATCH_SIZE),
                desc=f"  Шаг {step_num} (Запись в БД)",
                total=total_batches
            )

            for i in batch_progress:

                batch = objects_to_update[i:i + self.BATCH_SIZE]

                model_class.objects.bulk_update(
                    batch,
                    ['price', 'stock']
                )

            logger.info(
                f"  ...[OK] BATCH-ЗАПИСЬ в БД завершена.")

        return count
