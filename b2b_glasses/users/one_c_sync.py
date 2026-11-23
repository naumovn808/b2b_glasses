import logging
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.db.models import Q

from api.one_c_client import OneCClient
from users.models import Company, TelegramLinkToken, User

logger = logging.getLogger(__name__)


def _clean_str(value: Any, max_len: Optional[int] = None) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if max_len is not None:
        return text[:max_len]
    return text


def _extract_names(contact_person: Dict[str, Any]) -> tuple[str, str]:
    first_name = _clean_str(contact_person.get("first_name"), 150)
    last_name = _clean_str(contact_person.get("last_name"), 150)
    if not first_name and not last_name:
        full_name = _clean_str(contact_person.get("full_name"))
        if full_name:
            parts = full_name.split()
            last_name = parts[0][:150] if len(parts) > 1 else ""
            first_name = (" ".join(parts[1:]) if len(parts) > 1 else parts[0])[:150]
    return first_name, last_name


def upsert_customers_from_1c(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Создаёт или обновляет компании (Company) и пользователей (User) из данных 1С.
    Используется как для вебхука POST /api/v1/webhooks/1c/customers/,
    так и для периодической сверки GET /v1/customers.
    """
    results: List[Dict[str, Any]] = []

    for entry in items:
        if not isinstance(entry, dict):
            continue

        id_1c = _clean_str(entry.get("id_1c"), 255)
        company_name = _clean_str(entry.get("company_name"), 255)
        if not id_1c:
            logger.warning("[1C Customers Sync] Пропущен элемент без id_1c: %s", entry)
            continue

        if not company_name:
            company_name = (
                _clean_str(entry.get("partner_name"), 255)
                or f"Контрагент {id_1c[:8]}"
            )

        is_active = bool(entry.get("is_active", True))
        inn = _clean_str(entry.get("inn"), 64)
        partner_id_1c = _clean_str(entry.get("partner_id_1c"), 255) or None
        partner_name = _clean_str(entry.get("partner_name"), 255)
        head_partner_id_1c = _clean_str(entry.get("head_partner_id_1c"), 255) or None
        head_partner_name = _clean_str(entry.get("head_partner_name"), 255)

        contact = entry.get("contact_person") or {}
        phone = _clean_str(contact.get("phone"), 20)
        email = _clean_str(contact.get("email"), 254)
        first_name, last_name = _extract_names(contact)

        with transaction.atomic():
            company = Company.objects.filter(external_id=id_1c).first()
            if company is None:
                # Аккуратно подвязываем существующую компанию без external_id, если имя совпадает
                company = Company.objects.filter(
                    name=company_name, external_id__isnull=True
                ).first()

            if company is None:
                company = Company.objects.create(
                    external_id=id_1c,
                    name=company_name,
                    inn=inn,
                    is_active=is_active,
                    partner_id_1c=partner_id_1c,
                    partner_name=partner_name,
                    head_partner_id_1c=head_partner_id_1c,
                    head_partner_name=head_partner_name,
                )
            else:
                company.external_id = id_1c
                company.name = company_name
                company.inn = inn
                company.is_active = is_active
                company.partner_id_1c = partner_id_1c
                company.partner_name = partner_name
                company.head_partner_id_1c = head_partner_id_1c
                company.head_partner_name = head_partner_name
                company.save()

            user: Optional[User] = None
            telegram_link_token: Optional[str] = None

            if phone:
                user = User.objects.filter(
                    Q(phone_number=phone) | Q(username=phone)
                ).first()

                if user is None:
                    user = User(
                        username=phone,
                        phone_number=phone,
                        company=company,
                        first_name=first_name,
                        last_name=last_name,
                        email=email or None,
                        is_active=is_active,
                    )
                    user.set_unusable_password()
                    user.save()
                else:
                    user.company = company
                    user.phone_number = phone
                    if first_name:
                        user.first_name = first_name
                    if last_name:
                        user.last_name = last_name
                    if email:
                        user.email = email
                    user.is_active = is_active
                    user.save()

                token_obj = TelegramLinkToken.objects.filter(user=user).first()
                if token_obj is None and not user.telegram_id:
                    token_obj, _ = TelegramLinkToken.objects.get_or_create(user=user)
                if token_obj is not None:
                    telegram_link_token = str(token_obj.token)
            else:
                # Если контрагент деактивирован и у него нет телефона в выгрузке,
                # деактивируем связанных с компанией пользователей.
                if not is_active:
                    User.objects.filter(company=company, is_superuser=False).update(
                        is_active=False
                    )

        results.append(
            {
                "id_1c": id_1c,
                "company_id_site": company.pk,
                "user_id_site": user.pk if user else None,
                "telegram_link_token": telegram_link_token,
            }
        )

    return {
        "status": "success",
        "processed": len(results),
        "results": results,
    }


def sync_customers_from_1c(client: Optional[OneCClient] = None) -> Dict[str, Any]:
    api_client = client or OneCClient()
    data = api_client.get_customers()
    items = data.get("items") or []
    summary = upsert_customers_from_1c(items)
    logger.info(
        "[1C Customers Sync] Обработано контрагентов: %s (получено %s).",
        summary["processed"],
        len(items),
    )
    return summary

