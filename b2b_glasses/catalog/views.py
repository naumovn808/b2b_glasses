import logging
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsBot
from .models import Frame, Lens, LensSeries
from .serializers import FrameSerializer, LensSerializer, LensSeriesSerializer
from .filters import FrameFilter, LensFilter
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from users.models import User

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Brand, FrameMaterial, FrameShape, FrameType, FrameGender, FrameAgeGroup
from .serializers import (
    BrandSerializer, FrameMaterialSerializer, FrameShapeSerializer,
    FrameTypeSerializer, FrameGenderSerializer, FrameAgeGroupSerializer
)

logger = logging.getLogger(__name__)


def check_user_status_sync(telegram_id: str) -> bool:
    if not telegram_id:
        return False
    return User.objects.filter(telegram_id=telegram_id, is_active=True).exists()

# ---
# Views для ОПРАВ (ДЛЯ САЙТА И TWA)
# ---


# --- ИЗМЕНЕНИЕ: Добавлена 'page_size' в Swagger ---
frame_params = [
    openapi.Parameter('brand', openapi.IN_QUERY,
                      description="ID Бренда или список ID (напр. ?brand=1 или ?brand=1,3,5)", type=openapi.TYPE_STRING),
    openapi.Parameter('material', openapi.IN_QUERY,
                      description="ID Материала или список ID (напр. ?material=1,2)", type=openapi.TYPE_STRING),
    openapi.Parameter('shape', openapi.IN_QUERY,
                      description="ID Формы или список ID", type=openapi.TYPE_STRING),
    openapi.Parameter('type', openapi.IN_QUERY,
                      description="ID Типа или список ID", type=openapi.TYPE_STRING),
    openapi.Parameter('gender', openapi.IN_QUERY,
                      description="ID Пола или список ID", type=openapi.TYPE_STRING),
    openapi.Parameter('age_group', openapi.IN_QUERY,
                      description="ID Возрастной группы или список ID", type=openapi.TYPE_STRING),
    openapi.Parameter('price__gte', openapi.IN_QUERY,
                      description="Цена 'больше или равна'", type=openapi.TYPE_NUMBER),
    openapi.Parameter('price__lte', openapi.IN_QUERY,
                      description="Цена 'меньше или равна'", type=openapi.TYPE_NUMBER),
    openapi.Parameter('search', openapi.IN_QUERY,
                      description="Поиск по Имени, Артикулу или Бренду", type=openapi.TYPE_STRING),
    openapi.Parameter(
        'page_size', openapi.IN_QUERY,
        description="Кол-во элементов на странице (по умолч: 5, макс: 100)",
        type=openapi.TYPE_INTEGER
    )
]
# ---


class FrameListView(generics.ListAPIView):
    queryset = Frame.objects.filter(stock__gt=0)
    serializer_class = FrameSerializer
    filterset_class = FrameFilter
    permission_classes = [IsAuthenticated | IsBot]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('name', 'sku', 'brand__name')

    @swagger_auto_schema(
        tags=['Catalog (Каталог)'],
        operation_summary="1. Получить список ОПРАВ (с фильтрами)",
        # --- ИЗМЕНЕНО: Возвращаем manual_parameters ---
        manual_parameters=frame_params
    )
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            telegram_id = request.query_params.get('telegram_id')
            if not check_user_status_sync(telegram_id):
                logger.warning(
                    f"Доступ к FrameListView ЗАПРЕЩЕН (IsBot, но плохой telegram_id: {telegram_id})")
                return Response(
                    {"error": "Доступ запрещен. Пользователь не найден или неактивен."},
                    status=status.HTTP_403_FORBIDDEN
                )
        return super().get(request, *args, **kwargs)


class FrameFilterOptionsView(APIView):
    permission_classes = [IsAuthenticated | IsBot]

    @swagger_auto_schema(
        tags=['Catalog (Каталог)'],
        operation_summary="2. Получить опции фильтров для ОПРАВ",
        operation_description="Возвращает ВСЕ доступные Бренды, Материалы, Формы и т.д."
    )
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            telegram_id = request.query_params.get('telegram_id')
            if not check_user_status_sync(telegram_id):
                logger.warning(
                    f"Доступ к FrameFilterOptionsView ЗАПРЕЩЕН (IsBot, но плохой telegram_id: {telegram_id})")
                return Response(
                    {"error": "Доступ запрещен. Пользователь не найден или неактивен."},
                    status=status.HTTP_403_FORBIDDEN
                )
        data = {
            'brands': BrandSerializer(Brand.objects.all(), many=True).data,
            'materials': FrameMaterialSerializer(FrameMaterial.objects.all(), many=True).data,
            'shapes': FrameShapeSerializer(FrameShape.objects.all(), many=True).data,
            'types': FrameTypeSerializer(FrameType.objects.all(), many=True).data,
            'genders': FrameGenderSerializer(FrameGender.objects.all(), many=True).data,
            'age_groups': FrameAgeGroupSerializer(FrameAgeGroup.objects.all(), many=True).data
        }
        return Response(data)

# ---
# Views для ЛИНЗ (ДЛЯ САЙТА И БОТА)
# ---


# --- ИЗМЕНЕНИЕ: Добавлена 'page_size' в Swagger ---
lens_params = [
    openapi.Parameter('series', openapi.IN_QUERY,
                      description="ID Серии или список ID (напр. ?series=1 или ?series=1,2)", type=openapi.TYPE_STRING),
    openapi.Parameter('sph', openapi.IN_QUERY,
                      description="Значение Сферы или список (напр. ?sph=-1.25)", type=openapi.TYPE_STRING),
    openapi.Parameter('cyl', openapi.IN_QUERY,
                      description="Значение Цилиндра или список (напр. ?cyl=0.50)", type=openapi.TYPE_STRING),
    openapi.Parameter('dia', openapi.IN_QUERY,
                      description="Значение Диаметра или список (напр. ?dia=70)", type=openapi.TYPE_STRING),
    openapi.Parameter('search', openapi.IN_QUERY,
                      description="Поиск по Имени Серии или ID из 1С", type=openapi.TYPE_STRING),
    openapi.Parameter(
        'page_size', openapi.IN_QUERY,
        description="Кол-во элементов на странице (по умолч: 5, макс: 100)",
        type=openapi.TYPE_INTEGER
    )
]
# ---


class LensListView(generics.ListAPIView):
    queryset = Lens.objects.filter(stock__gt=0).select_related('series')
    serializer_class = LensSerializer
    filterset_class = LensFilter
    permission_classes = [IsAuthenticated | IsBot]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('series__name', 'id_1c')

    # --- ИЗМЕНЕНО: @swagger_auto_schema (добавлен manual_parameters) ---
    @swagger_auto_schema(
        tags=['Catalog (Каталог)'],
        operation_summary="3. Получить список ЛИНЗ (с фильтрами)",
        manual_parameters=lens_params
    )
    # ---
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            telegram_id = request.query_params.get('telegram_id')
            if not check_user_status_sync(telegram_id):
                logger.warning(
                    f"Доступ к LensListView ЗАПРЕЩЕН (IsBot, но плохой telegram_id: {telegram_id})")
                return Response(
                    {"error": "Доступ запрещен. Пользователь не найден или неактивен."},
                    status=status.HTTP_403_FORBIDDEN
                )
        return super().get(request, *args, **kwargs)


class LensOptionsView(APIView):
    permission_classes = [IsAuthenticated | IsBot]

    @swagger_auto_schema(
        tags=['Catalog (Каталог)'],
        operation_summary="4. Получить опции фильтров для ЛИНЗ",
        operation_description="Возвращает ВСЕ доступные Серии, SPH, CYL и DIA."
    )
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            telegram_id = request.query_params.get('telegram_id')
            if not check_user_status_sync(telegram_id):
                logger.warning(
                    f"Доступ к LensOptionsView ЗАПРЕЩЕН (IsBot, но плохой telegram_id: {telegram_id})")
                return Response(
                    {"error": "Доступ запрещен. Пользователь не найден или неактивен."},
                    status=status.HTTP_403_FORBIDDEN
                )

        series_data = LensSeriesSerializer(
            LensSeries.objects.all(), many=True).data
        sph_values = Lens.objects.values_list(
            'sph', flat=True).distinct().order_by('sph')
        cyl_values = Lens.objects.values_list(
            'cyl', flat=True).distinct().order_by('cyl')
        dia_values = Lens.objects.values_list(
            'dia', flat=True).distinct().order_by('dia')

        data = {
            'series': series_data,
            'sph': list(sph_values),
            'cyl': list(cyl_values),
            'dia': list(dia_values)
        }
        return Response(data)
