from decimal import Decimal
import uuid

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import (
    Brand,
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


class Command(BaseCommand):
    help = "Добавляет демо-данные для каталога: фильтры, оправы, серии и линзы."

    def handle(self, *args, **options):
        run_id = uuid.uuid4()

        with transaction.atomic():
            brands = self._create_items(
                Brand,
                ["Minimo", "Retrio Brook", "Learts", "Vagabond", "Abby", "Optika Pro"],
            )
            materials = self._create_items(
                FrameMaterial,
                ["Ацетат", "Металл", "Комбинированный", "Титан", "TR-90"],
            )
            shapes = self._create_items(
                FrameShape,
                ["Квадратная", "Круглая", "Овальная", "Авиатор", "Кошачий глаз"],
            )
            types = self._create_items(
                FrameType,
                ["Ободковая", "Полуободковая", "Безободковая"],
            )
            genders = self._create_items(
                FrameGender,
                ["Мужская", "Женская", "Унисекс"],
            )
            ages = self._create_items(
                FrameAgeGroup,
                ["Взрослые", "Подростковые", "Детские"],
            )

            frames = [
                {
                    "id_1c": "DEMO-FRAME-001",
                    "name": "Minimo Classic 2101 C1",
                    "sku": "MIN-2101-C1",
                    "barcode": "2000000000011",
                    "brand": brands["Minimo"],
                    "material": materials["Ацетат"],
                    "shape": shapes["Квадратная"],
                    "type": types["Ободковая"],
                    "gender": genders["Унисекс"],
                    "age_group": ages["Взрослые"],
                    "color_title": "Черный глянец",
                    "color_hex": "#111111",
                    "size_a": "52.00",
                    "size_b": "39.00",
                    "size_d": "18.00",
                    "size_temple": "145.00",
                    "price": "420000.00",
                    "stock": 18,
                },
                {
                    "id_1c": "DEMO-FRAME-002",
                    "name": "Retrio Brook Round 714 C3",
                    "sku": "RB-714-C3",
                    "barcode": "2000000000028",
                    "brand": brands["Retrio Brook"],
                    "material": materials["Металл"],
                    "shape": shapes["Круглая"],
                    "type": types["Ободковая"],
                    "gender": genders["Унисекс"],
                    "age_group": ages["Взрослые"],
                    "color_title": "Золото",
                    "color_hex": "#d4af37",
                    "size_a": "49.00",
                    "size_b": "45.00",
                    "size_d": "20.00",
                    "size_temple": "140.00",
                    "price": "385000.00",
                    "stock": 12,
                },
                {
                    "id_1c": "DEMO-FRAME-003",
                    "name": "Learts Soft Oval 503 C2",
                    "sku": "LEA-503-C2",
                    "barcode": "2000000000035",
                    "brand": brands["Learts"],
                    "material": materials["Комбинированный"],
                    "shape": shapes["Овальная"],
                    "type": types["Полуободковая"],
                    "gender": genders["Женская"],
                    "age_group": ages["Взрослые"],
                    "color_title": "Бордовый",
                    "color_hex": "#7d1f2d",
                    "size_a": "51.00",
                    "size_b": "38.00",
                    "size_d": "17.00",
                    "size_temple": "140.00",
                    "price": "455000.00",
                    "stock": 9,
                },
                {
                    "id_1c": "DEMO-FRAME-004",
                    "name": "Vagabond Air Titanium 880 C4",
                    "sku": "VGB-880-C4",
                    "barcode": "2000000000042",
                    "brand": brands["Vagabond"],
                    "material": materials["Титан"],
                    "shape": shapes["Авиатор"],
                    "type": types["Безободковая"],
                    "gender": genders["Мужская"],
                    "age_group": ages["Взрослые"],
                    "color_title": "Графит",
                    "color_hex": "#4a4d52",
                    "size_a": "54.00",
                    "size_b": "42.00",
                    "size_d": "18.00",
                    "size_temple": "145.00",
                    "price": "690000.00",
                    "stock": 7,
                },
                {
                    "id_1c": "DEMO-FRAME-005",
                    "name": "Abby Junior Flex 120 C5",
                    "sku": "ABB-120-C5",
                    "barcode": "2000000000059",
                    "brand": brands["Abby"],
                    "material": materials["TR-90"],
                    "shape": shapes["Овальная"],
                    "type": types["Ободковая"],
                    "gender": genders["Унисекс"],
                    "age_group": ages["Детские"],
                    "color_title": "Синий матовый",
                    "color_hex": "#1f4f8f",
                    "size_a": "46.00",
                    "size_b": "34.00",
                    "size_d": "16.00",
                    "size_temple": "130.00",
                    "price": "260000.00",
                    "stock": 22,
                },
                {
                    "id_1c": "DEMO-FRAME-006",
                    "name": "Optika Pro Cat Eye 332 C7",
                    "sku": "OP-332-C7",
                    "barcode": "2000000000066",
                    "brand": brands["Optika Pro"],
                    "material": materials["Ацетат"],
                    "shape": shapes["Кошачий глаз"],
                    "type": types["Ободковая"],
                    "gender": genders["Женская"],
                    "age_group": ages["Взрослые"],
                    "color_title": "Черепаховый",
                    "color_hex": "#7a4b2a",
                    "size_a": "53.00",
                    "size_b": "40.00",
                    "size_d": "16.00",
                    "size_temple": "140.00",
                    "price": "510000.00",
                    "stock": 14,
                },
            ]

            for frame in frames:
                defaults = {
                    **frame,
                    "run_id": run_id,
                    "size_a": Decimal(frame["size_a"]),
                    "size_b": Decimal(frame["size_b"]),
                    "size_d": Decimal(frame["size_d"]),
                    "size_temple": Decimal(frame["size_temple"]),
                    "price": Decimal(frame["price"]),
                }
                id_1c = defaults.pop("id_1c")
                frame_obj, _ = Frame.objects.update_or_create(
                    id_1c=id_1c,
                    defaults=defaults,
                )
                self._sync_colors(
                    frame_obj,
                    [
                        (frame["color_title"], frame["color_hex"]),
                    ],
                )

            series = self._create_items(
                LensSeries,
                [
                    "ClearVision Standard 1.50",
                    "ClearVision Blue Block 1.56",
                    "OptiLux Aspheric 1.60",
                    "Premium Drive 1.67",
                ],
            )

            lens_rows = []
            for series_name, base_price in [
                ("ClearVision Standard 1.50", Decimal("85000.00")),
                ("ClearVision Blue Block 1.56", Decimal("145000.00")),
                ("OptiLux Aspheric 1.60", Decimal("220000.00")),
                ("Premium Drive 1.67", Decimal("340000.00")),
            ]:
                for sph in [Decimal("-2.00"), Decimal("-1.00"), Decimal("0.00"), Decimal("1.00"), Decimal("2.00")]:
                    for cyl in [Decimal("0.00"), Decimal("-0.50"), Decimal("-1.00")]:
                        lens_rows.append(
                            {
                                "id_1c": f"DEMO-LENS-{series_name[:3].upper()}-{sph}-{cyl}".replace(" ", "-"),
                                "series": series[series_name],
                                "sph": sph,
                                "cyl": cyl,
                                "dia": 70,
                                "price": base_price + abs(sph * Decimal("10000.00")) + abs(cyl * Decimal("12000.00")),
                                "stock": 20,
                            }
                        )

            for lens in lens_rows:
                defaults = {**lens, "run_id": run_id}
                id_1c = defaults.pop("id_1c")
                lens_obj, _ = Lens.objects.update_or_create(
                    id_1c=id_1c,
                    defaults=defaults,
                )
                self._sync_colors(lens_obj, [("Прозрачные", "#ffffff")])

        self.stdout.write(self.style.SUCCESS("Демо-данные каталога добавлены/обновлены."))
        self.stdout.write(f"Оправы: {Frame.objects.count()}")
        self.stdout.write(f"Линзы: {Lens.objects.count()}")

    def _create_items(self, model, names):
        items = {}
        for name in names:
            item, _ = model.objects.get_or_create(name=name)
            items[name] = item
        return items

    def _sync_colors(self, product, colors):
        product.colors.all().delete()
        for index, (name, hex_value) in enumerate(colors):
            product_color = ProductColor(
                name=name,
                hex_value=hex_value,
                order=index,
            )
            product_color.product = product
            product_color.save()
