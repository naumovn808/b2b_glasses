import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.auth import OneCBasicAuthentication
from catalog.one_c_sync import apply_stock_updates
from users.one_c_sync import upsert_customers_from_1c

logger = logging.getLogger(__name__)


class OneCStocksWebhookView(APIView):
    """
    Вебхук от 1С для точечного обновления остатков и цен в реальном времени.
    POST /api/v1/webhooks/1c/stocks/
    """

    authentication_classes = [OneCBasicAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["1C Webhooks"],
        operation_summary="Вебхук обновления остатков и цен из 1С",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "reason": openapi.Schema(type=openapi.TYPE_STRING),
                "currency": openapi.Schema(type=openapi.TYPE_STRING),
                "items": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id_1c": openapi.Schema(type=openapi.TYPE_STRING),
                            "stock": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "price": openapi.Schema(type=openapi.TYPE_NUMBER),
                        },
                        required=["id_1c", "stock"],
                    ),
                ),
            },
            required=["items"],
        ),
        responses={200: "Остатки обновлены", 400: "Некорректный формат", 401: "Не авторизован"},
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, dict):
            return Response(
                {
                    "status": "error",
                    "error_code": "INVALID_JSON",
                    "message": "Ожидался JSON-объект.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        items = data.get("items")
        if not isinstance(items, list):
            return Response(
                {
                    "status": "error",
                    "error_code": "VALIDATION_ERROR",
                    "message": "Поле 'items' обязательно и должно быть массивом.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = data.get("reason", "")
        currency = data.get("currency", "")
        result = apply_stock_updates(items)

        logger.info(
            "[1C Webhook Stocks] reason=%s currency=%s received=%s updated_frames=%s updated_lenses=%s not_found=%s",
            reason,
            currency,
            len(items),
            result["updated_frames"],
            result["updated_lenses"],
            len(result["not_found"]),
        )

        return Response(
            {
                "status": "success",
                "updated_frames": result["updated_frames"],
                "updated_lenses": result["updated_lenses"],
                "not_found": result["not_found"],
            },
            status=status.HTTP_200_OK,
        )


class OneCCustomersWebhookView(APIView):
    """
    Вебхук от 1С для создания/обновления контрагентов и пользователей.
    POST /api/v1/webhooks/1c/customers/
    Поддерживает как {"items": [...]}, так и одиночный объект контрагента.
    """

    authentication_classes = [OneCBasicAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["1C Webhooks"],
        operation_summary="Вебхук создания/обновления контрагентов из 1С",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "items": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT),
                )
            },
        ),
        responses={200: "Контрагенты обработаны", 400: "Некорректный формат", 401: "Не авторизован"},
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data, dict) and "items" in data:
            items = data.get("items")
            if not isinstance(items, list):
                return Response(
                    {
                        "status": "error",
                        "error_code": "VALIDATION_ERROR",
                        "message": "Поле 'items' должно быть массивом.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif isinstance(data, dict) and data.get("id_1c"):
            items = [data]
        else:
            return Response(
                {
                    "status": "error",
                    "error_code": "VALIDATION_ERROR",
                    "message": "Ожидался объект с массивом 'items' или одиночный контрагент с 'id_1c'.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        summary = upsert_customers_from_1c(items)
        logger.info(
            "[1C Webhook Customers] received=%s processed=%s",
            len(items),
            summary["processed"],
        )
        return Response(summary, status=status.HTTP_200_OK)

