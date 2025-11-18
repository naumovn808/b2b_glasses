import ftplib
import logging
from io import BytesIO
from django.conf import settings
from .models import Order
from .xml import generate_order_xml

# --- ИМПОРТЫ ДЛЯ APSCHEDULER ---
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone  # <--- ДОБАВЛЕН ИМПОРТ
# ---

logger = logging.getLogger(__name__)

# Папка на FTP (из вашего ТЗ)
REMOTE_ORDER_PATH = "/Заказы/"


def upload_order_to_ftp(order_id: int):
    """
    Основная "работа". 
    1. Находит заказ
    2. Генерирует XML
    3. Загружает на FTP
    """
    logger.info(f"[FTP Upload Job] Запуск для Заказа #{order_id}...")

    try:
        order = Order.objects.get(pk=order_id, status='pending')
    except Order.DoesNotExist:
        logger.error(
            f"[FTP Upload Job] ОШИБКА: Заказ #{order_id} не найден или уже не 'pending'.")
        return

    # 1. Генерируем "красивую" XML-строку
    try:
        xml_string = generate_order_xml(order)

        # --- ИСПРАВЛЕНИЕ: КОДИРУЕМ С BOM-МЕТКОЙ ---
        # 'utf-8-sig' автоматически добавит "магические"
        # байты \xef\xbb\xbf в начало файла.
        xml_bytes = xml_string.encode('utf-8-sig')
        # ---

    except Exception as e:
        logger.critical(
            f"[FTP Upload Job] ОШИБКА: Не удалось сгенерировать XML для Заказа #{order_id}: {e}", exc_info=True)
        return

    # 2. Подключаемся и загружаем
    file_name = f"order_{order_id}.xml"
    remote_full_path = f"{REMOTE_ORDER_PATH.rstrip('/')}/{file_name}"

    try:
        logger.info(
            f"[FTP Upload Job] Подключаюсь к FTP {settings.FTP_HOST} для {file_name}...")

        with ftplib.FTP(encoding='utf-8') as ftp:
            ftp.connect(settings.FTP_HOST, settings.FTP_PORT)
            ftp.login(settings.FTP_USER, settings.FTP_PASS)
            ftp.sendcmd("OPTS UTF8 ON")
            ftp.encoding = "utf-8"
            ftp.set_pasv(True)

            logger.info(
                f"[FTP Upload Job] ...Успешно. Перехожу в {REMOTE_ORDER_PATH}")

            try:
                ftp.cwd(REMOTE_ORDER_PATH)
            except ftplib.error_perm:
                logger.warning(
                    f"[FTP Upload Job] Папка {REMOTE_ORDER_PATH} не найдена. Пытаюсь создать...")
                ftp.mkd(REMOTE_ORDER_PATH)
                ftp.cwd(REMOTE_ORDER_PATH)

            logger.info(f"[FTP Upload Job] ...Загружаю {file_name}...")

            with BytesIO(xml_bytes) as file_buffer:
                ftp.storbinary(f'STOR {file_name}', file_buffer)

            logger.info(
                f"[FTP Upload Job] УСПЕХ: Файл {remote_full_path} успешно загружен.")

    except Exception as e:
        logger.critical(
            f"[FTP Upload Job] ОШИБКА: Не удалось загрузить {file_name} на FTP: {e}", exc_info=True)


# --- Функция, которую будет "видеть" APScheduler ---

def schedule_ftp_upload(order: Order):
    """
    Добавляет задачу в базу данных. 
    ВЫПОЛНЯТЬ её будет отдельный контейнер b2b_scheduler.
    """
    try:

        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            upload_order_to_ftp,
            'date',
            run_date=timezone.now(),
            args=[order.pk],
            id=f"upload_order_{order.pk}_{timezone.now().timestamp()}",
            replace_existing=False,
            misfire_grace_time=60 * 30
        )

        logger.info(
            f"[Checkout] Заказ #{order.pk} успешно добавлен в очередь задач (DB).")

    except Exception as e:
        logger.error(
            f"[Checkout] ОШИБКА: не удалось поставить Заказ #{order.pk} в очередь: {e}")
