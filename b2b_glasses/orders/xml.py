import xml.etree.ElementTree as ET
# --- 1. ВОЗВРАЩАЕМ MINIDOM ---
from xml.dom import minidom
# ---
from .models import Order
from catalog.models import Frame, Lens
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def generate_order_xml(order: Order) -> str:
    """
    Генерирует XML-строку (в формате CommerceML 2.04) 
    для одного Заказа.
    (v12 - Возвращаем minidom для "красоты")
    """
    logger.info(f"Начинаю генерацию XML для Заказа #{order.pk}...")

    now = timezone.now()
    order_date = now.strftime("%Y-%m-%d")
    order_time = now.strftime("%H:%M:%S")

    # --- 1. <КоммерческаяИнформация> (Корень) ---
    root = ET.Element("КоммерческаяИнформация")
    root.set("ВерсияСхемы", "2.04")
    root.set("ДатаФормирования", now.isoformat(timespec='seconds'))

    # --- 2. <Документ> ---
    doc = ET.SubElement(root, "Документ")
    ET.SubElement(doc, "Ид").text = str(order.pk)
    ET.SubElement(doc, "Номер").text = f"Т{order.pk:05d}"
    ET.SubElement(doc, "Дата").text = order_date
    ET.SubElement(doc, "ХозОперация").text = "Заказ товара"
    ET.SubElement(doc, "Роль").text = "Продавец"
    ET.SubElement(doc, "Валюта").text = "UZS"
    ET.SubElement(doc, "Курс").text = "1.0000"
    ET.SubElement(doc, "Сумма").text = f"{order.total_price:.2f}"
    ET.SubElement(doc, "Время").text = order_time
    ET.SubElement(
        doc, "Комментарий").text = f"Заказ #{order.pk} от {order.user.username}"

    # --- 3. <Контрагенты> (Пользователь) ---
    kontragenty = ET.SubElement(doc, "Контрагенты")
    kontragent = ET.SubElement(kontragenty, "Контрагент")
    ET.SubElement(kontragent, "Ид").text = str(order.user.pk)
    ET.SubElement(kontragent, "Наименование").text = order.user.username
    ET.SubElement(kontragent, "Роль").text = "Покупатель"
    full_name = f"{order.user.first_name or ''} {order.user.last_name or ''}".strip()
    if not full_name:
        full_name = order.user.username
    ET.SubElement(kontragent, "ПолноеНаименование").text = full_name
    if order.user.phone_number:
        kontakty = ET.SubElement(kontragent, "Контакты")
        kontakt = ET.SubElement(kontakty, "Контакт")
        ET.SubElement(kontakt, "Тип").text = "Телефон"
        ET.SubElement(kontakt, "Значение").text = order.user.phone_number

    # --- 4. <Товары> ---
    tovary = ET.SubElement(doc, "Товары")

    for item in order.items.all():
        product = item.product

        tovar = ET.SubElement(tovary, "Товар")

        if isinstance(product, Frame):
            vid_nomenklatury = "Оправы"
        elif isinstance(product, Lens):
            vid_nomenklatury = "Очковые линзы"
        else:
            vid_nomenklatury = "Товар"

        ET.SubElement(tovar, "Ид").text = product.id_1c
        ET.SubElement(tovar, "Артикул").text = getattr(product, 'sku', '')
        ET.SubElement(tovar, "Наименование").text = getattr(
            product, 'name', str(product))
        ET.SubElement(
            tovar, "БазоваяЕдиница",
            Код="796", НаименованиеПолное="Штука"
        ).text = "шт"
        ET.SubElement(
            tovar, "ЦенаЗаЕдиницу").text = f"{item.price_at_order:.2f}"
        ET.SubElement(tovar, "Количество").text = str(item.quantity)
        ET.SubElement(tovar, "Сумма").text = f"{item.total_price:.2f}"

        rekvizity = ET.SubElement(tovar, "ЗначенияРеквизитов")
        rek_vid = ET.SubElement(rekvizity, "ЗначениеРеквизита")
        ET.SubElement(rek_vid, "Наименование").text = "ВидНоменклатуры"
        ET.SubElement(rek_vid, "Значение").text = vid_nomenklatury
        rek_tip = ET.SubElement(rekvizity, "ЗначениеРеквизита")
        ET.SubElement(rek_tip, "Наименование").text = "ТипНоменклатуры"
        ET.SubElement(rek_tip, "Значение").text = "Товар"

    # --- 5. <ЗначенияРеквизитов> (Документа) ---
    doc_rekvizity = ET.SubElement(doc, "ЗначенияРеквизитов")
    rek_nomer = ET.SubElement(doc_rekvizity, "ЗначениеРеквизита")
    ET.SubElement(rek_nomer, "Наименование").text = "НомерЗаказаНаСайте"
    ET.SubElement(rek_nomer, "Значение").text = f"Т{order.pk:05d}"
    rek_data = ET.SubElement(doc_rekvizity, "ЗначениеРеквизита")
    ET.SubElement(rek_data, "Наименование").text = "ДатаЗаказаНаСайте"
    ET.SubElement(rek_data, "Значение").text = now.isoformat(
        timespec='seconds')
    rek_ud = ET.SubElement(doc_rekvizity, "ЗначениеРеквизита")
    ET.SubElement(rek_ud, "Наименование").text = "ПометкаУдаления"
    ET.SubElement(rek_ud, "Значение").text = "false"
    rek_pr = ET.SubElement(doc_rekvizity, "ЗначениеРеквизита")
    ET.SubElement(rek_pr, "Наименование").text = "Проведен"
    ET.SubElement(rek_pr, "Значение").text = "true"

    # --- 6. Преобразуем в "сырую" строку (не байты) ---
    xml_str = ET.tostring(root, encoding='unicode', method='xml')

    # --- 7. Используем minidom для "красоты" (отступов) ---
    # (Это больше не "сломает" кодировку, т.к. мы работаем со строками)
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")

    logger.info(f"XML (красивый) для Заказа #{order.pk} успешно сгенерирован.")

    # Возвращаем "красивую" СТРОКУ
    return pretty_xml_str
