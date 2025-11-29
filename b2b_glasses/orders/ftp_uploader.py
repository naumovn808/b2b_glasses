import ftplib
import logging
import threading
from io import BytesIO
from django.conf import settings
from .models import Order
from .xml import generate_order_xml

logger = logging.getLogger(__name__)

REMOTE_ORDER_PATH = "/Заказы/"


def upload_order_to_ftp(order_id: int):
    """
    Выгрузка заказа на FTP.
    """
    # Закрываем старое соединение с БД для корректной работы в потоке
    from django.db import connection
    connection.close()

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        logger.error(f"[FTP Worker] Заказ #{order_id} не найден.")
        return

    try:
        xml_string = generate_order_xml(order)
        xml_bytes = xml_string.encode('utf-8-sig')
    except Exception as e:
        logger.error(f"[FTP Worker] Ошибка генерации XML: {e}")
        return

    file_name = f"order_{order_id}.xml"

    try:
        with ftplib.FTP() as ftp:
            ftp.connect(settings.FTP_HOST, settings.FTP_PORT, timeout=30)
            ftp.login(settings.FTP_USER, settings.FTP_PASS)
            ftp.sendcmd("OPTS UTF8 ON")
            ftp.encoding = "utf-8"
            ftp.set_pasv(True)

            try:
                ftp.cwd(REMOTE_ORDER_PATH)
            except ftplib.error_perm:
                ftp.mkd(REMOTE_ORDER_PATH)
                ftp.cwd(REMOTE_ORDER_PATH)

            with BytesIO(xml_bytes) as file_buffer:
                ftp.storbinary(f'STOR {file_name}', file_buffer)

            logger.info(f"[FTP Worker] УСПЕХ: Файл {file_name} загружен.")

    except Exception as e:
        logger.error(f"[FTP Worker] Ошибка FTP: {e}")


def schedule_ftp_upload(order: Order):
    """
    Запускает выгрузку сразу же, в фоновом потоке.
    """
    try:
        thread = threading.Thread(target=upload_order_to_ftp, args=(order.pk,))
        thread.start()
        logger.info(f"[Checkout] Запущена выгрузка Заказа #{order.pk}")
    except Exception as e:
        logger.error(f"[Checkout] Не удалось запустить поток: {e}")
