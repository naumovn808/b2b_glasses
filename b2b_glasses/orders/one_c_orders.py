import logging
from typing import Any, Dict, Optional

from django.conf import settings
from django.utils import timezone

from api.one_c_client import OneCClient
from catalog.models import Frame, Lens
from orders.models import Order

logger = logging.getLogger(__name__)


class OrderCustomerConfigError(ValueError):
    """У пользователя заказа не привязана компания с GUID 1С."""


def build_order_payload(order: Order) -> Dict[str, Any]:
    """
    Формирует JSON-тело запроса для POST /v1/orders на стороне 1С.
    """
    user = order.user
    company = getattr(user, "company", None)
    company_id_1c = getattr(company, "external_id", None) if company else None
    if not company_id_1c:
        raise OrderCustomerConfigError(
            "У вашей компании не указан идентификатор 1С (company_id_1c). "
            "Обратитесь к менеджеру."
        )

    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username
    phone = user.phone_number or ""
    email = user.email or ""
    created_dt = timezone.localtime(order.created_at or timezone.now())

    items_payload = []
    for item in order.items.all():
        product = item.product
        if product is None or not getattr(product, "id_1c", None):
            raise ValueError(
                f"Позиция заказа #{item.pk} не содержит корректный id_1c товара."
            )

        if isinstance(product, Frame):
            category_type = "Оправы"
            product_name = product.name
            product_sku = product.sku or ""
        elif isinstance(product, Lens):
            category_type = "Очковые линзы"
            product_name = product.name or str(product)
            product_sku = product.sku or ""
        else:
            category_type = "Товар"
            product_name = str(product)
            product_sku = getattr(product, "sku", "") or ""

        items_payload.append(
            {
                "id_1c": product.id_1c,
                "sku": product_sku,
                "name": product_name,
                "category_type": category_type,
                "unit": "шт",
                "unit_code": "796",
                "quantity": item.quantity,
                "price": float(item.price_at_order),
                "total_price": float(item.total_price),
            }
        )

    currency = getattr(settings, "ONE_C_ORDER_CURRENCY", "UZS")
    order_number = f"Т{order.pk:05d}"

    return {
        "order_id": order.pk,
        "order_number": order_number,
        "created_at": created_dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "currency": currency,
        "total_price": float(order.total_price),
        "comment": f"Заказ #{order.pk} от пользователя {phone or user.username}",
        "customer": {
            "user_id_site": user.pk,
            "company_id_1c": company_id_1c,
            "company_name": company.name,
            "contact_name": full_name,
            "phone": phone,
            "email": email,
        },
        "items": items_payload,
    }


def submit_order_to_1c(
    order: Order,
    client: Optional[OneCClient] = None,
) -> Dict[str, Any]:
    """
    Синхронно отправляет заказ в 1С (POST /v1/orders).
    Возвращает JSON-ответ 1С (при 200 или 201) либо выбрасывает OneCAPIError / OneCConnectionError.
    """
    payload = build_order_payload(order)
    api_client = client or OneCClient()
    logger.info(
        "[1C Order Push] Отправка заказа #%s (%s) в 1С, позиций=%s, сумма=%s %s",
        order.pk,
        payload["order_number"],
        len(payload["items"]),
        payload["total_price"],
        payload["currency"],
    )
    response_data = api_client.create_order(payload)
    logger.info(
        "[1C Order Push] Заказ #%s принят 1С: order_id_1c=%s doc_number_1c=%s",
        order.pk,
        response_data.get("order_id_1c"),
        response_data.get("doc_number_1c"),
    )
    return response_data

