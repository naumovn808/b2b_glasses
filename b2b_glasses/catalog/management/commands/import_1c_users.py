import os
import xml.etree.ElementTree as ET
import ftplib
from pathlib import Path
import logging
import uuid
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from users.models import Company, User

logger = logging.getLogger(__name__)

NS = {"cml": "urn:1C.ru:commerceml_2"}
FILES_TO_DOWNLOAD = ["kontragents.xml"]  # Предполагаемый файл контрагентов
REMOTE_PATH = "/Выгрузка/webdata"


class Command(BaseCommand):
    help = "Подключается к FTP, скачивает XML-файл контрагентов и импортирует их в БД."

    def handle(self, *args, **options):
        self.current_run_id = uuid.uuid4()
        logger.info(f"--- [RUN ID: {self.current_run_id}] ---")

        temp_dir = Path(settings.BASE_DIR) / "temp_xml"
        try:
            os.makedirs(temp_dir, exist_ok=True)
            logger.info(f"Создана временная папка: {temp_dir}")
        except Exception as e:
            logger.critical(f"Не удалось создать временную папку: {e}")
            raise CommandError(f"Не удалось создать временную папку: {e}")

        try:
            logger.info(
                f"Подключаюсь к FTP: {settings.FTP_HOST}:{settings.FTP_PORT} (encoding=utf-8)..."
            )
            with ftplib.FTP(encoding="utf-8") as ftp:
                ftp.connect(settings.FTP_HOST, settings.FTP_PORT)
                ftp.login(settings.FTP_USER, settings.FTP_PASS)
                ftp.sendcmd("OPTS UTF8 ON")
                ftp.encoding = "utf-8"
                ftp.set_pasv(True)
                logger.info("Успешно подключен к FTP (UTF-8).")
                logger.info(f"Перехожу в папку: {REMOTE_PATH}")
                ftp.cwd(REMOTE_PATH)
                logger.info(f"Скачиваю {len(FILES_TO_DOWNLOAD)} файла...")
                downloaded_count = 0

                for filename in tqdm(FILES_TO_DOWNLOAD, desc="Скачивание XML"):
                    local_path = os.path.join(temp_dir, filename)
                    try:
                        with open(local_path, "wb") as f:
                            ftp.retrbinary(f"RETR {filename}", f.write)
                        downloaded_count += 1
                    except Exception as e:
                        logger.critical(
                            f"  [КРИТИЧЕСКАЯ ОШИБКА] Не удалось скачать {filename}: {e}"
                        )
                        logger.critical(
                            "Процесс импорта будет остановлен. База данных НЕ будет затронута."
                        )
                        raise CommandError(f"Ошибка скачивания файла: {e}")

                if downloaded_count < len(FILES_TO_DOWNLOAD):
                    logger.critical(
                        f"ОШИБКА: Скачано {downloaded_count} из {len(FILES_TO_DOWNLOAD)} необходимых файлов."
                    )
                    raise CommandError("Не все файлы были успешно скачаны.")

                logger.info(f"Успешно скачано {downloaded_count} файла.")

        except ftplib.error_perm as e:
            logger.critical(f'Ошибка FTP (Папка "{REMOTE_PATH}" не найдена?): {e}')
            raise CommandError(f"Ошибка FTP: {e}")
        except Exception as e:
            if isinstance(e, CommandError):
                raise
            logger.critical(f"Ошибка FTP (адрес/порт?): {e}")
            raise CommandError(f"Ошибка FTP: {e}")

        xml_path = str(temp_dir)
        self.file_kontragents = os.path.join(xml_path, "kontragents.xml")

        # Pre-flight проверка
        logger.info('Запуск "Pre-flight" проверки скачанных XML-файлов...')
        try:
            if not os.path.exists(self.file_kontragents):
                logger.critical(
                    f"Файл {self.file_kontragents} отсутствует после скачивания."
                )
                raise FileNotFoundError(f"Файл {self.file_kontragents} отсутствует.")
            ET.parse(self.file_kontragents)
            logger.info("...[OK] XML-файл контрагентов корректен и готов к импорту.")
        except ET.ParseError as e:
            logger.critical(f"Ошибка парсинга XML: {e}")
            raise CommandError(f"Ошибка парсинга XML: {e}")
        except Exception as e:
            logger.critical(f"Неизвестная ошибка при проверке: {e}")
            raise CommandError(f"Ошибка проверки файлов: {e}")

        logger.info("--- Начало импорта контрагентов 1C ---")

        try:
            with transaction.atomic():
                logger.info("Импорт контрагентов...")
                count = self._import_kontragents()
                logger.info(f"Обработано {count} контрагентов.")

            logger.info(
                f"--- Импорт контрагентов (RUN ID: {self.current_run_id}) успешно завершен! ---"
            )

        except Exception as e:
            logger.critical(f"Произошла неизвестная ошибка импорта: {e}", exc_info=True)
            raise CommandError(f"Импорт прерван из-за ошибки: {e}")

    def _find_text(self, element, path, default=""):
        tag = element.find(path, NS)
        if tag is not None and tag.text is not None:
            return tag.text.strip()
        return default

    def _import_kontragents(self):
        try:
            tree = ET.parse(self.file_kontragents)
            root = tree.getroot()
        except FileNotFoundError:
            logger.error(f"ОШИБКА: не найден {self.file_kontragents}")
            raise

        kontragents_tag = root.find("cml:Контрагенты", NS)
        if kontragents_tag is None:
            logger.warning("Не найден <Контрагенты>.")
            return 0

        count = 0
        for kontragent in kontragents_tag.findall("cml:Контрагент", NS):
            kontragent_id = self._find_text(kontragent, "cml:Ид")
            name = self._find_text(kontragent, "cml:Наименование")

            if not name:
                logger.warning(
                    f"Пропущен контрагент без наименования (Ид: {kontragent_id})"
                )
                continue

            # Создаем или обновляем компанию
            company, created = Company.objects.get_or_create(
                name=name, defaults={"external_id": kontragent_id}
            )
            if not created:
                company.external_id = kontragent_id
                company.save()

            # Парсим контакты
            contacts = {}
            contacts_tag = kontragent.find("cml:Контакты", NS)
            if contacts_tag:
                for contact in contacts_tag.findall("cml:Контакт", NS):
                    contact_type = self._find_text(contact, "cml:Тип")
                    contact_value = self._find_text(contact, "cml:Значение")
                    if contact_type and contact_value:
                        contacts[contact_type] = contact_value

            # Извлекаем данные пользователя
            email = contacts.get("Почта", "")
            phone = contacts.get("Телефон", "")
            full_name = contacts.get("ФИО", "")

            if not email or not full_name:
                logger.warning(
                    f"Пропущен пользователь для контрагента {name}: нет email или ФИО"
                )
                continue

            # Разделяем ФИО на first_name и last_name (просто предположим first last)
            name_parts = full_name.split()
            first_name = name_parts[0] if name_parts else ""
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            # Создаем или обновляем пользователя
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone_number": phone,
                    "company": company,
                    "username": phone,
                },
            )
            if not created:
                user.first_name = first_name
                user.last_name = last_name
                user.phone_number = phone
                user.company = company
                user.save()

            count += 1

        return count
