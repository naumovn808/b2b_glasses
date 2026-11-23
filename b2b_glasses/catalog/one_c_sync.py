import logging
import uuid
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from api.one_c_client import OneCClient
from catalog.models import (
    Brand,
    Color,
    ColorGroup,
    Frame,
    FrameAgeGroup,
    FrameGender,
    FrameMaterial,
    FrameShape,
    FrameType,
    Lens,
    LensSeries,
    ProductColor,
)

logger = logging.getLogger(__name__)

COLOR_GROUP_KEYWORDS: Tuple[Tuple[str, str], ...] = (
    # Фиолетовый (проверяем раньше розового)
    ("фиолет", "Фиолетовый"),
    ("purple", "Фиолетовый"),
    ("purpple", "Фиолетовый"),
    ("violet", "Фиолетовый"),
    ("lilac", "Фиолетовый"),
    ("mauve", "Фиолетовый"),
    ("lavender", "Фиолетовый"),
    ("aubergine", "Фиолетовый"),
    ("plum", "Фиолетовый"),
    # Оранжевый
    ("оранж", "Оранжевый"),
    ("orange", "Оранжевый"),
    ("tangarine", "Оранжевый"),
    ("tangerine", "Оранжевый"),
    ("apricot", "Оранжевый"),
    ("coral", "Оранжевый"),
    # Черный
    ("черн", "Черный"),
    ("black", "Черный"),
    ("blaack", "Черный"),
    ("noir", "Черный"),
    ("onyx", "Черный"),
    ("ebony", "Черный"),
    ("nero", "Черный"),
    # Белый
    ("бел", "Белый"),
    ("white", "Белый"),
    ("blanc", "Белый"),
    ("marshmallow", "Белый"),
    ("pearl", "Белый"),
    # Золотой
    ("золот", "Золотой"),
    ("gold", "Золотой"),
    ("желт", "Золотой"),
    ("yellow", "Золотой"),
    ("lemon", "Золотой"),
    ("messing", "Золотой"),
    ("brass", "Золотой"),
    # Серебряный
    ("серебр", "Серебряный"),
    ("silver", "Серебряный"),
    # Красный / Бордовый
    ("красн", "Красный"),
    ("red", "Красный"),
    ("борд", "Красный"),
    ("burgundy", "Красный"),
    ("bordeaux", "Красный"),
    ("cherry", "Красный"),
    ("wine", "Красный"),
    ("ruby", "Красный"),
    ("crimson", "Красный"),
    ("cayenne", "Красный"),
    ("terrakotta", "Красный"),
    ("terracotta", "Красный"),
    ("rouge", "Красный"),
    # Синий / Голубой / Бирюзовый
    ("син", "Синий"),
    ("голуб", "Синий"),
    ("blue", "Синий"),
    ("bue", "Синий"),
    ("bleu", "Синий"),
    ("navy", "Синий"),
    ("petrol", "Синий"),
    ("denim", "Синий"),
    ("jeans", "Синий"),
    ("turquoise", "Синий"),
    ("turqoise", "Синий"),
    ("teal", "Синий"),
    ("azure", "Синий"),
    ("cyan", "Синий"),
    ("cobalt", "Синий"),
    ("indigo", "Синий"),
    ("aqua", "Синий"),
    # Зеленый
    ("зелен", "Зеленый"),
    ("green", "Зеленый"),
    ("olive", "Зеленый"),
    ("oliv", "Зеленый"),
    ("sage", "Зеленый"),
    ("khaki", "Зеленый"),
    ("mint", "Зеленый"),
    ("avocado", "Зеленый"),
    ("eucalyptus", "Зеленый"),
    ("emerald", "Зеленый"),
    ("vert", "Зеленый"),
    # Коричневый / Черепаховый / Гавана
    ("коричн", "Коричневый"),
    ("brown", "Коричневый"),
    ("havana", "Коричневый"),
    ("havanna", "Коричневый"),
    ("tortoise", "Коричневый"),
    ("черепах", "Коричневый"),
    ("demi", "Коричневый"),
    ("chocolate", "Коричневый"),
    ("bronze", "Коричневый"),
    ("mokka", "Коричневый"),
    ("mocha", "Коричневый"),
    ("espresso", "Коричневый"),
    ("coffee", "Коричневый"),
    ("kamel", "Коричневый"),
    ("camel", "Коричневый"),
    ("zimt", "Коричневый"),
    ("caramel", "Коричневый"),
    ("amber", "Коричневый"),
    ("cognac", "Коричневый"),
    ("marron", "Коричневый"),
    # Серый / Графит / Ганметал
    ("сер", "Серый"),
    ("grey", "Серый"),
    ("gray", "Серый"),
    ("gris", "Серый"),
    ("gun", "Серый"),
    ("anthrazit", "Серый"),
    ("anthracite", "Серый"),
    ("graphite", "Серый"),
    ("cement", "Серый"),
    ("concrete", "Серый"),
    ("asphalt", "Серый"),
    ("ruthenium", "Серый"),
    ("charcoal", "Серый"),
    ("smoke", "Серый"),
    ("slate", "Серый"),
    # Розовый
    ("розов", "Розовый"),
    ("pink", "Розовый"),
    ("rose", "Розовый"),
    ("fuchsia", "Розовый"),
    ("magenta", "Розовый"),
    ("blush", "Розовый"),
    # Бежевый
    ("беж", "Бежевый"),
    ("beige", "Бежевый"),
    ("sand", "Бежевый"),
    ("cream", "Бежевый"),
    ("nude", "Бежевый"),
    ("taupe", "Бежевый"),
    ("ivory", "Бежевый"),
    ("champagne", "Бежевый"),
    # Прозрачный
    ("прозрач", "Прозрачный"),
    ("crystal", "Прозрачный"),
    ("cristal", "Прозрачный"),
    ("kristall", "Прозрачный"),
    ("transparent", "Прозрачный"),
    ("transp", "Прозрачный"),
    ("clear", "Прозрачный"),
)


def _to_decimal(value: Any, default: Optional[Decimal] = None) -> Optional[Decimal]:
    if value is None or value == "":
        return default
    try:
        normalized = str(value).strip().replace(",", ".")
        return Decimal(normalized)
    except (InvalidOperation, ValueError, TypeError):
        return default


def _to_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    if value is None or value == "":
        return default
    try:
        return int(Decimal(str(value).strip().replace(",", ".")))
    except (InvalidOperation, ValueError, TypeError):
        return default


def _clean_str(value: Any, max_len: Optional[int] = None) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if max_len is not None:
        return text[:max_len]
    return text


def _get_or_create_cached(model_class, cache: Dict[str, Any], name: str):
    clean = _clean_str(name)
    if not clean:
        return None
    obj = cache.get(clean)
    if obj is None:
        obj, _ = model_class.objects.get_or_create(name=clean)
        cache[clean] = obj
    return obj


def assign_color_group(
    color_name: str, groups_cache: Dict[str, ColorGroup]
) -> Optional[ColorGroup]:
    name_lower = color_name.lower()
    for keyword, group_name in COLOR_GROUP_KEYWORDS:
        if keyword in name_lower:
            group = groups_cache.get(group_name)
            if group is not None:
                return group
    return groups_cache.get("Другое")


def _extract_frame_color_names(properties: Dict[str, Any]) -> List[str]:
    """
    Приоритет: properties.manufacturer_color (например, 'Blue'),
    fallback: properties.colors (например, ['C06']), если manufacturer_color не задан.
    """
    manufacturer_color = _clean_str(properties.get("manufacturer_color"), 255)
    if manufacturer_color:
        return [manufacturer_color]

    raw_colors = properties.get("colors") or []
    result: List[str] = []
    seen = set()
    for raw in raw_colors:
        cleaned = _clean_str(raw, 255)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result


def sync_frames_from_1c(
    client: Optional[OneCClient] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Постраничная синхронизация оправ из 1С (GET /v1/catalog/frames).
    Отсутствующие в выгрузке оправы не удаляются, а получают stock=0,
    чтобы сохранить загруженные вручную фото и историю заказов.
    """
    api_client = client or OneCClient()
    run_id = uuid.uuid4()

    brands_cache = {b.name: b for b in Brand.objects.all()}
    materials_cache = {m.name: m for m in FrameMaterial.objects.all()}
    shapes_cache = {s.name: s for s in FrameShape.objects.all()}
    types_cache = {t.name: t for t in FrameType.objects.all()}
    genders_cache = {g.name: g for g in FrameGender.objects.all()}
    ages_cache = {a.name: a for a in FrameAgeGroup.objects.all()}
    groups_cache = {g.name: g for g in ColorGroup.objects.all()}
    colors_cache = {c.name: c for c in Color.objects.select_related("group").all()}

    existing_map: Dict[str, int] = dict(Frame.objects.values_list("id_1c", "id"))
    frame_ct = ContentType.objects.get_for_model(Frame)

    update_fields = [
        "name",
        "sku",
        "barcode",
        "brand",
        "material",
        "shape",
        "type",
        "gender",
        "age_group",
        "size_a",
        "size_b",
        "size_d",
        "size_temple",
        "price",
        "stock",
        "run_id",
    ]

    created_total = 0
    updated_total = 0
    skipped_total = 0
    pages_processed = 0
    expected_count: Optional[int] = None
    currency: Optional[str] = None

    for page_data in api_client.iter_frames(limit=limit):
        pages_processed += 1
        if expected_count is None:
            expected_count = page_data.get("count")
        if currency is None:
            currency = page_data.get("currency")

        items = page_data.get("items") or []
        if not items:
            continue

        # Дедупликация в рамках страницы (последний выигрывает)
        dedup_items: Dict[str, Dict[str, Any]] = {}
        for item in items:
            id_1c = _clean_str(item.get("id_1c"), 100)
            if not id_1c:
                skipped_total += 1
                continue
            dedup_items[id_1c] = item

        to_create: List[Frame] = []
        to_update: List[Frame] = []
        page_colors_by_id_1c: Dict[str, List[str]] = {}

        for id_1c, item in dedup_items.items():
            props = item.get("properties") or {}
            sizes = props.get("sizes") or {}

            price = _to_decimal(item.get("price"), Decimal("0.00"))
            stock = max(0, _to_int(item.get("stock"), 0) or 0)

            fields_data = {
                "name": _clean_str(item.get("name"), 500),
                "sku": _clean_str(item.get("sku"), 255),
                "barcode": _clean_str(item.get("barcode"), 50) or None,
                "brand": _get_or_create_cached(Brand, brands_cache, item.get("brand")),
                "material": _get_or_create_cached(
                    FrameMaterial, materials_cache, props.get("material")
                ),
                "shape": _get_or_create_cached(
                    FrameShape, shapes_cache, props.get("shape")
                ),
                "type": _get_or_create_cached(
                    FrameType, types_cache, props.get("frame_type")
                ),
                "gender": _get_or_create_cached(
                    FrameGender, genders_cache, props.get("gender")
                ),
                "age_group": _get_or_create_cached(
                    FrameAgeGroup, ages_cache, props.get("age_group")
                ),
                "size_a": _to_decimal(sizes.get("size_a")),
                "size_b": _to_decimal(sizes.get("size_b")),
                "size_d": _to_decimal(sizes.get("size_d")),
                "size_temple": _to_decimal(sizes.get("size_temple")),
                "price": price,
                "stock": stock,
                "run_id": run_id,
            }

            existing_id = existing_map.get(id_1c)
            if existing_id is not None:
                to_update.append(Frame(id=existing_id, id_1c=id_1c, **fields_data))
            else:
                to_create.append(Frame(id_1c=id_1c, **fields_data))

            color_names = _extract_frame_color_names(props)
            if color_names:
                page_colors_by_id_1c[id_1c] = color_names

        with transaction.atomic():
            if to_create:
                Frame.objects.bulk_create(to_create, batch_size=500)
                created_total += len(to_create)
                new_id_1cs = [obj.id_1c for obj in to_create]
                for db_id_1c, db_id in Frame.objects.filter(
                    id_1c__in=new_id_1cs
                ).values_list("id_1c", "id"):
                    existing_map[db_id_1c] = db_id

            if to_update:
                Frame.objects.bulk_update(to_update, update_fields, batch_size=500)
                updated_total += len(to_update)

            if page_colors_by_id_1c:
                frame_ids_with_colors = [
                    existing_map[id_1c]
                    for id_1c in page_colors_by_id_1c
                    if id_1c in existing_map
                ]
                ProductColor.objects.filter(
                    content_type=frame_ct,
                    object_id__in=frame_ids_with_colors,
                ).delete()

                new_product_colors: List[ProductColor] = []
                for id_1c, color_names in page_colors_by_id_1c.items():
                    frame_pk = existing_map.get(id_1c)
                    if not frame_pk:
                        continue
                    for idx, color_name in enumerate(color_names):
                        color_obj = colors_cache.get(color_name)
                        if color_obj is None:
                            color_obj, _ = Color.objects.get_or_create(name=color_name)
                            if not color_obj.group or color_obj.group.name == "Другое":
                                group = assign_color_group(color_name, groups_cache)
                                if group is not None and color_obj.group_id != group.id:
                                    color_obj.group = group
                                    color_obj.save(update_fields=["group"])
                            colors_cache[color_name] = color_obj
                        elif not color_obj.group or color_obj.group.name == "Другое":
                            group = assign_color_group(color_name, groups_cache)
                            if group is not None and color_obj.group_id != group.id:
                                color_obj.group = group
                                color_obj.save(update_fields=["group"])

                        new_product_colors.append(
                            ProductColor(
                                content_type=frame_ct,
                                object_id=frame_pk,
                                color=color_obj,
                                name=color_name,
                                order=idx,
                            )
                        )

                if new_product_colors:
                    ProductColor.objects.bulk_create(new_product_colors, batch_size=500)

        logger.info(
            "[1C Frames Sync] Страница %s обработана (создано=%s, обновлено=%s).",
            page_data["page"],
            len(to_create),
            len(to_update),
        )

    stale_zeroed = 0
    if created_total + updated_total > 0 or expected_count == 0:
        stale_zeroed = (
            Frame.objects.exclude(run_id=run_id)
            .filter(stock__gt=0)
            .update(stock=0)
        )

    summary = {
        "pages": pages_processed,
        "created": created_total,
        "updated": updated_total,
        "skipped": skipped_total,
        "stale_zeroed": stale_zeroed,
        "currency": currency,
        "expected_count": expected_count,
    }
    logger.info("[1C Frames Sync] Завершено: %s", summary)
    return summary


def sync_lenses_from_1c(
    client: Optional[OneCClient] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Постраничная синхронизация линз из 1С (GET /v1/catalog/lenses).
    Отсутствующие в выгрузке линзы получают stock=0 без физического удаления.
    """
    api_client = client or OneCClient()
    run_id = uuid.uuid4()

    series_cache = {s.name: s for s in LensSeries.objects.all()}
    groups_cache = {g.name: g for g in ColorGroup.objects.all()}
    colors_cache = {c.name: c for c in Color.objects.select_related("group").all()}
    existing_map: Dict[str, int] = dict(Lens.objects.values_list("id_1c", "id"))
    lens_ct = ContentType.objects.get_for_model(Lens)

    update_fields = [
        "name",
        "sku",
        "barcode",
        "series",
        "sph",
        "cyl",
        "dia",
        "price",
        "stock",
        "run_id",
    ]

    created_total = 0
    updated_total = 0
    skipped_total = 0
    pages_processed = 0
    expected_count: Optional[int] = None
    currency: Optional[str] = None

    for page_data in api_client.iter_lenses(limit=limit):
        pages_processed += 1
        if expected_count is None:
            expected_count = page_data.get("count")
        if currency is None:
            currency = page_data.get("currency")

        items = page_data.get("items") or []
        if not items:
            continue

        dedup_items: Dict[str, Dict[str, Any]] = {}
        for item in items:
            id_1c = _clean_str(item.get("id_1c"), 100)
            if not id_1c:
                skipped_total += 1
                continue
            dedup_items[id_1c] = item

        to_create: List[Lens] = []
        to_update: List[Lens] = []
        page_colors_by_id_1c: Dict[str, List[str]] = {}

        for id_1c, item in dedup_items.items():
            full_name = _clean_str(item.get("name"), 500)
            series_name = _clean_str(item.get("series"), 500) or full_name
            sph = _to_decimal(item.get("sph"))
            cyl = _to_decimal(item.get("cyl"), Decimal("0.00"))
            dia = _to_int(item.get("dia"), default=None)

            if not series_name or sph is None:
                skipped_total += 1
                continue

            series = _get_or_create_cached(LensSeries, series_cache, series_name)
            price = _to_decimal(item.get("price"), Decimal("0.00"))
            stock = max(0, _to_int(item.get("stock"), 0) or 0)

            fields_data = {
                "name": full_name,
                "sku": _clean_str(item.get("sku"), 255),
                "barcode": _clean_str(item.get("barcode"), 50) or None,
                "series": series,
                "sph": sph,
                "cyl": cyl if cyl is not None else Decimal("0.00"),
                "dia": dia,
                "price": price,
                "stock": stock,
                "run_id": run_id,
            }

            existing_id = existing_map.get(id_1c)
            if existing_id is not None:
                to_update.append(Lens(id=existing_id, id_1c=id_1c, **fields_data))
            else:
                to_create.append(Lens(id_1c=id_1c, **fields_data))

            raw_lens_colors = item.get("colors") or []
            if raw_lens_colors:
                cleaned_colors = [
                    _clean_str(c, 255) for c in raw_lens_colors if _clean_str(c, 255)
                ]
                if cleaned_colors:
                    page_colors_by_id_1c[id_1c] = cleaned_colors

        with transaction.atomic():
            if to_create:
                Lens.objects.bulk_create(to_create, batch_size=500)
                created_total += len(to_create)
                new_id_1cs = [obj.id_1c for obj in to_create]
                for db_id_1c, db_id in Lens.objects.filter(
                    id_1c__in=new_id_1cs
                ).values_list("id_1c", "id"):
                    existing_map[db_id_1c] = db_id

            if to_update:
                Lens.objects.bulk_update(to_update, update_fields, batch_size=500)
                updated_total += len(to_update)

            if page_colors_by_id_1c:
                lens_ids_with_colors = [
                    existing_map[id_1c]
                    for id_1c in page_colors_by_id_1c
                    if id_1c in existing_map
                ]
                ProductColor.objects.filter(
                    content_type=lens_ct,
                    object_id__in=lens_ids_with_colors,
                ).delete()

                new_lens_colors: List[ProductColor] = []
                for id_1c, color_names in page_colors_by_id_1c.items():
                    lens_pk = existing_map.get(id_1c)
                    if not lens_pk:
                        continue
                    for idx, color_name in enumerate(color_names):
                        color_obj = colors_cache.get(color_name)
                        if color_obj is None:
                            color_obj, _ = Color.objects.get_or_create(name=color_name)
                            if not color_obj.group or color_obj.group.name == "Другое":
                                group = assign_color_group(color_name, groups_cache)
                                if group is not None and color_obj.group_id != group.id:
                                    color_obj.group = group
                                    color_obj.save(update_fields=["group"])
                            colors_cache[color_name] = color_obj
                        new_lens_colors.append(
                            ProductColor(
                                content_type=lens_ct,
                                object_id=lens_pk,
                                color=color_obj,
                                name=color_name,
                                order=idx,
                            )
                        )
                if new_lens_colors:
                    ProductColor.objects.bulk_create(new_lens_colors, batch_size=500)

        if pages_processed % 10 == 0 or len(items) < (limit or 500):
            logger.info(
                "[1C Lenses Sync] Страница %s обработана (всего создано=%s, обновлено=%s).",
                page_data["page"],
                created_total,
                updated_total,
            )

    stale_zeroed = 0
    if created_total + updated_total > 0 or expected_count == 0:
        stale_zeroed = (
            Lens.objects.exclude(run_id=run_id)
            .filter(stock__gt=0)
            .update(stock=0)
        )

    summary = {
        "pages": pages_processed,
        "created": created_total,
        "updated": updated_total,
        "skipped": skipped_total,
        "stale_zeroed": stale_zeroed,
        "currency": currency,
        "expected_count": expected_count,
    }
    logger.info("[1C Lenses Sync] Завершено: %s", summary)
    return summary


def apply_stock_updates(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Точечное обновление остатков и цен по списку позиций с id_1c.
    Используется как для вебхука POST /api/v1/webhooks/1c/stocks/,
    так и для updated_stocks из ответа POST /v1/orders.
    """
    if not items:
        return {
            "updated_frames": 0,
            "updated_lenses": 0,
            "not_found": [],
        }

    # Сохраняем порядок, при дубликатах внутри пачки побеждает последнее значение
    normalized: Dict[str, Dict[str, Any]] = {}
    for entry in items:
        if not isinstance(entry, dict):
            continue
        id_1c = _clean_str(entry.get("id_1c"), 100)
        if not id_1c:
            continue
        normalized[id_1c] = entry

    if not normalized:
        return {
            "updated_frames": 0,
            "updated_lenses": 0,
            "not_found": [],
        }

    id_list = list(normalized.keys())
    frames_by_id = Frame.objects.in_bulk(id_list, field_name="id_1c")
    remaining_ids = [i for i in id_list if i not in frames_by_id]
    lenses_by_id = (
        Lens.objects.in_bulk(remaining_ids, field_name="id_1c") if remaining_ids else {}
    )

    frames_to_update: List[Frame] = []
    lenses_to_update: List[Lens] = []
    not_found: List[str] = []

    for id_1c, entry in normalized.items():
        obj = frames_by_id.get(id_1c) or lenses_by_id.get(id_1c)
        if obj is None:
            not_found.append(id_1c)
            continue

        changed = False
        if "stock" in entry and entry["stock"] is not None:
            stock_val = _to_int(entry["stock"])
            if stock_val is not None:
                obj.stock = max(0, stock_val)
                changed = True

        if "price" in entry and entry["price"] is not None:
            price_val = _to_decimal(entry["price"])
            if price_val is not None and price_val >= 0:
                obj.price = price_val
                changed = True

        if not changed:
            continue

        if isinstance(obj, Frame):
            frames_to_update.append(obj)
        else:
            lenses_to_update.append(obj)

    with transaction.atomic():
        if frames_to_update:
            Frame.objects.bulk_update(
                frames_to_update, ["stock", "price"], batch_size=500
            )
        if lenses_to_update:
            Lens.objects.bulk_update(
                lenses_to_update, ["stock", "price"], batch_size=500
            )

    return {
        "updated_frames": len(frames_to_update),
        "updated_lenses": len(lenses_to_update),
        "not_found": not_found,
    }

