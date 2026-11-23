import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "b2b_glasses.settings")
django.setup()

from catalog.models import Color, ColorGroup
from catalog.one_c_sync import assign_color_group

STANDARD_GROUPS = [
    ("Черный", "#1A1A1A", 1),
    ("Серый", "#808080", 2),
    ("Серебряный", "#C0C0C0", 3),
    ("Белый", "#FFFFFF", 4),
    ("Прозрачный", "#E6F4FA", 5),
    ("Бежевый", "#E8D5B7", 6),
    ("Золотой", "#E6B800", 7),
    ("Коричневый", "#7B4B2A", 8),
    ("Оранжевый", "#FF8C00", 9),
    ("Красный", "#D32F2F", 10),
    ("Розовый", "#F48FB1", 11),
    ("Фиолетовый", "#7E57C2", 12),
    ("Синий", "#1976D2", 13),
    ("Зеленый", "#2E7D32", 14),
    ("Другое", "#B0BEC5", 100),
]


def run():
    groups_cache = {}
    for name, hex_value, order in STANDARD_GROUPS:
        group, created = ColorGroup.objects.get_or_create(
            name=name,
            defaults={"hex_value": hex_value, "order": order},
        )
        if not created and (group.hex_value != hex_value or group.order != order):
            group.hex_value = hex_value
            group.order = order
            group.save(update_fields=["hex_value", "order"])
        groups_cache[name] = group

    updated = 0
    other_count = 0
    for color in Color.objects.select_related("group").all():
        target = assign_color_group(color.name, groups_cache)
        if target is None:
            continue
        if target.name == "Другое":
            other_count += 1
        if color.group_id != target.id:
            color.group = target
            color.save(update_fields=["group"])
            updated += 1

    print(f"Updated group for {updated} colors. Remaining in 'Другое': {other_count}.")


if __name__ == "__main__":
    run()
