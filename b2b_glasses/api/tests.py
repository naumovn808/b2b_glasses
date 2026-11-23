import base64
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api.one_c_client import OneCAPIError, OneCConnectionError
from catalog.models import ColorGroup, Frame, Lens, LensSeries, ProductImage
from catalog.one_c_sync import sync_frames_from_1c, sync_lenses_from_1c
from orders.models import Order, OrderItem
from users.models import Company, TelegramLinkToken, User


def _basic_auth_header(username: str, password: str) -> str:
    raw = f"{username}:{password}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


@override_settings(
    ONE_C_WEBHOOK_USER="1c_hook",
    ONE_C_WEBHOOK_PASSWORD="secret_password",
    ONE_C_ORDER_CURRENCY="UZS",
)
class OneCIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.auth_header = _basic_auth_header("1c_hook", "secret_password")
        ColorGroup.objects.get_or_create(name="Синий", defaults={"hex_value": "#0000FF"})
        ColorGroup.objects.get_or_create(name="Другое", defaults={"hex_value": "#CCCCCC"})

    def test_webhooks_require_valid_basic_auth(self):
        resp_no_auth = self.client.post(
            "/api/v1/webhooks/1c/stocks/",
            {"reason": "stock_changed", "items": []},
            format="json",
        )
        self.assertEqual(resp_no_auth.status_code, 401)

        resp_bad_auth = self.client.post(
            "/api/v1/webhooks/1c/stocks/",
            {"reason": "stock_changed", "items": []},
            format="json",
            HTTP_AUTHORIZATION=_basic_auth_header("1c_hook", "wrong"),
        )
        self.assertEqual(resp_bad_auth.status_code, 401)

    def test_stocks_webhook_updates_frames_and_lenses(self):
        series = LensSeries.objects.create(name="MultiView Max")
        frame = Frame.objects.create(
            id_1c="frame-guid-1",
            name="OPAL Frame",
            sku="SKU-1",
            price=Decimal("20.00"),
            stock=5,
        )
        lens = Lens.objects.create(
            id_1c="lens-guid-1#char-1",
            name="Lens Full Name",
            series=series,
            sph=Decimal("-0.50"),
            cyl=Decimal("-0.50"),
            dia=70,
            price=Decimal("10.00"),
            stock=3,
        )

        resp = self.client.post(
            "/api/v1/webhooks/1c/stocks/",
            {
                "reason": "stock_changed",
                "currency": "USD",
                "items": [
                    {"id_1c": "frame-guid-1", "stock": 0, "price": 25.9},
                    {"id_1c": "lens-guid-1#char-1", "stock": 8},
                    {"id_1c": "missing-guid", "stock": 4},
                ],
            },
            format="json",
            HTTP_AUTHORIZATION=self.auth_header,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "success")
        self.assertEqual(resp.data["updated_frames"], 1)
        self.assertEqual(resp.data["updated_lenses"], 1)
        self.assertEqual(resp.data["not_found"], ["missing-guid"])

        frame.refresh_from_db()
        lens.refresh_from_db()
        self.assertEqual(frame.stock, 0)
        self.assertEqual(frame.price, Decimal("25.90"))
        self.assertEqual(lens.stock, 8)
        self.assertEqual(lens.price, Decimal("10.00"))

    def test_customers_webhook_creates_updates_and_deactivates(self):
        payload = {
            "items": [
                {
                    "id_1c": "748d5374-5062-11f1-b0f9-e5e035715444",
                    "company_name": "ООО «DIVOOPTICA»",
                    "inn": "123456789",
                    "is_active": True,
                    "partner_id_1c": "partner-1",
                    "partner_name": "DIVO",
                    "head_partner_id_1c": "head-1",
                    "head_partner_name": "DIVO HEAD",
                    "contact_person": {
                        "full_name": "Иванов Иван",
                        "first_name": "Иван",
                        "last_name": "Иванов",
                        "phone": "+998946764459",
                        "email": "",
                    },
                }
            ]
        }

        resp = self.client.post(
            "/api/v1/webhooks/1c/customers/",
            payload,
            format="json",
            HTTP_AUTHORIZATION=self.auth_header,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["processed"], 1)
        row = resp.data["results"][0]
        self.assertEqual(row["id_1c"], "748d5374-5062-11f1-b0f9-e5e035715444")
        self.assertIsNotNone(row["company_id_site"])
        self.assertIsNotNone(row["user_id_site"])
        self.assertIsNotNone(row["telegram_link_token"])

        user = User.objects.get(pk=row["user_id_site"])
        self.assertTrue(user.is_active)
        self.assertEqual(user.company.external_id, "748d5374-5062-11f1-b0f9-e5e035715444")
        self.assertTrue(TelegramLinkToken.objects.filter(user=user).exists())

        # Деактивация через одиночный объект
        single_payload = dict(payload["items"][0], is_active=False)
        resp2 = self.client.post(
            "/api/v1/webhooks/1c/customers/",
            single_payload,
            format="json",
            HTTP_AUTHORIZATION=self.auth_header,
        )
        self.assertEqual(resp2.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertFalse(user.company.is_active)

    def test_sync_frames_maps_manufacturer_color_and_preserves_images(self):
        old_frame = Frame.objects.create(
            id_1c="stale-frame-1",
            name="Old Frame",
            sku="OLD-1",
            price=Decimal("10.00"),
            stock=5,
        )
        ProductImage.objects.create(product=old_frame, image="products/test.jpg")

        mock_client = MagicMock()
        mock_client.iter_frames.return_value = iter(
            [
                {
                    "page": 1,
                    "count": 1,
                    "currency": "USD",
                    "items": [
                        {
                            "id_1c": "1dc9255e-58c0-11f0-b0e4-ee81ce5b1c14",
                            "sku": "DAAA042C06",
                            "name": "OPAL Avengers",
                            "barcode": "3608301269866",
                            "brand": "OPAL",
                            "price": 25.9,
                            "stock": 2,
                            "properties": {
                                "gender": "Мужская",
                                "age_group": "Детская",
                                "material": "Acetate",
                                "shape": "Barrel",
                                "frame_type": "Fullrim",
                                "colors": ["C06"],
                                "manufacturer_color": "Blue",
                                "sizes": {
                                    "size_a": 43,
                                    "size_b": 30.2,
                                    "size_d": None,
                                    "size_temple": 125,
                                },
                            },
                            "images": [],
                        }
                    ],
                }
            ]
        )

        summary = sync_frames_from_1c(client=mock_client)
        self.assertEqual(summary["created"], 1)
        self.assertEqual(summary["stale_zeroed"], 1)

        # Старая оправа не удалена (сохранена с фото), а обнулена
        old_frame.refresh_from_db()
        self.assertEqual(old_frame.stock, 0)
        self.assertEqual(old_frame.images.count(), 1)

        new_frame = Frame.objects.get(id_1c="1dc9255e-58c0-11f0-b0e4-ee81ce5b1c14")
        self.assertIsNone(new_frame.size_d)
        pc = new_frame.colors.first()
        self.assertIsNotNone(pc)
        self.assertEqual(pc.name, "Blue")
        self.assertEqual(pc.color.group.name, "Синий")

    def test_sync_lenses_allows_null_dia_and_zero_price(self):
        mock_client = MagicMock()
        mock_client.iter_lenses.return_value = iter(
            [
                {
                    "page": 1,
                    "count": 1,
                    "currency": "USD",
                    "items": [
                        {
                            "id_1c": "lens-1#char-1",
                            "sku": "L-SKU",
                            "barcode": "",
                            "name": "150 ProtectAR+ MultiView Max (-00.50 cyl -00.50)",
                            "series": "MultiView Max",
                            "sph": "-0.50",
                            "cyl": "-0.50",
                            "dia": None,
                            "price": 0,
                            "stock": 1,
                            "colors": [],
                            "properties": {"index": "", "coating": ""},
                            "images": [],
                        }
                    ],
                }
            ]
        )

        summary = sync_lenses_from_1c(client=mock_client)
        self.assertEqual(summary["created"], 1)

        lens = Lens.objects.get(id_1c="lens-1#char-1")
        self.assertIsNone(lens.dia)
        self.assertEqual(lens.price, Decimal("0.00"))
        self.assertEqual(lens.name, "150 ProtectAR+ MultiView Max (-00.50 cyl -00.50)")

        # Проверяем, что LensOptionsView и LensListView не падают при dia=None и price=0
        resp_opts = self.client.get("/api/v1/catalog/lenses/options/")
        self.assertEqual(resp_opts.status_code, 200)
        self.assertEqual(resp_opts.data["dia"], [])

        resp_list = self.client.get("/api/v1/catalog/lenses/")
        self.assertEqual(resp_list.status_code, 200)
        self.assertEqual(resp_list.data["count"], 1)

    def test_cart_stock_checks_and_sync_checkout_flow(self):
        company = Company.objects.create(
            name="Test Optics", external_id="748d5374-5062-11f1-b0f9-e5e035715444"
        )
        user = User.objects.create_user(
            username="+998901234567",
            password="password123",
            phone_number="+998901234567",
            company=company,
        )
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        frame = Frame.objects.create(
            id_1c="1dc9255e-58c0-11f0-b0e4-ee81ce5b1c14",
            name="OPAL Avengers",
            sku="DAAA042C06",
            price=Decimal("330000.00"),
            stock=2,
        )

        # Попытка добавить больше остатка -> 400
        resp_over = self.client.post(
            "/api/v1/orders/cart/add/",
            {"product_type": "frame", "product_id": frame.pk, "quantity": 5},
            format="json",
        )
        self.assertEqual(resp_over.status_code, 400)

        # Добавляем корректное количество (2 шт)
        resp_add = self.client.post(
            "/api/v1/orders/cart/add/",
            {"product_type": "frame", "product_id": frame.pk, "quantity": 2},
            format="json",
        )
        self.assertEqual(resp_add.status_code, 201)

        # 1С отвечает 422 PRODUCT_OUT_OF_STOCK -> корзина остаётся CART, остаток обновляется до 1
        with patch("orders.views.submit_order_to_1c") as mock_submit:
            mock_submit.side_effect = OneCAPIError(
                message="Недостаточно остатка по ряду позиций",
                status_code=422,
                error_code="PRODUCT_OUT_OF_STOCK",
                payload={
                    "updated_stocks": [
                        {
                            "id_1c": frame.id_1c,
                            "requested": 2,
                            "stock": 1,
                        }
                    ]
                },
            )
            resp_oos = self.client.post("/api/v1/orders/cart/checkout/")
            self.assertEqual(resp_oos.status_code, 422)
            self.assertEqual(resp_oos.data["error_code"], "PRODUCT_OUT_OF_STOCK")

        frame.refresh_from_db()
        self.assertEqual(frame.stock, 1)
        cart = Order.objects.get(user=user)
        self.assertEqual(cart.status, Order.OrderStatus.CART)

        # Обновляем количество в корзине до 1 шт
        item = OrderItem.objects.get(order=cart)
        resp_patch = self.client.patch(
            f"/api/v1/orders/cart/items/{item.pk}/update/",
            {"quantity": 1},
            format="json",
        )
        self.assertEqual(resp_patch.status_code, 200)

        # При сетевой ошибке 1С -> 503, корзина не теряется
        with patch("orders.views.submit_order_to_1c") as mock_submit:
            mock_submit.side_effect = OneCConnectionError("Timeout", error_code="TIMEOUT")
            resp_503 = self.client.post("/api/v1/orders/cart/checkout/")
            self.assertEqual(resp_503.status_code, 503)

        # Успешное оформление в 1С -> 200, сохраняются id_1c и doc_number_1c, stock обновляется
        with patch("orders.views.submit_order_to_1c") as mock_submit:
            mock_submit.return_value = {
                "status": "success",
                "order_id_site": cart.pk,
                "order_id_1c": "9ba12345-58c0-11f0-b0e4-ee81ce5b1c14",
                "doc_number_1c": "0000-000482",
                "message": "Заказ успешно создан и проведен",
                "updated_stocks": [
                    {"id_1c": frame.id_1c, "stock": 0, "price": 25.9},
                ],
            }
            resp_ok = self.client.post("/api/v1/orders/cart/checkout/")
            self.assertEqual(resp_ok.status_code, 200)
            self.assertEqual(resp_ok.data["doc_number_1c"], "0000-000482")

        cart.refresh_from_db()
        frame.refresh_from_db()
        self.assertEqual(cart.status, Order.OrderStatus.PENDING)
        self.assertEqual(cart.id_1c, "9ba12345-58c0-11f0-b0e4-ee81ce5b1c14")
        self.assertEqual(cart.doc_number_1c, "0000-000482")
        self.assertEqual(frame.stock, 0)
