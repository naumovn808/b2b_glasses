# from rest_framework import generics
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import AllowAny
# from .models import Frame, Lens, LensSeries, Color, ColorGroup, Brand, FrameMaterial, FrameShape, FrameType, FrameGender, FrameAgeGroup, ProductColor
# from .serializers import (
#     FrameSerializer, LensSerializer, LensSeriesSerializer, ColorSerializer, ColorGroupSerializer,
#     BrandSerializer, FrameMaterialSerializer, FrameShapeSerializer,
#     FrameTypeSerializer, FrameGenderSerializer, FrameAgeGroupSerializer,
#     ProductColorSerializer
# )
# from .filters import FrameFilter, LensFilter
# from rest_framework.filters import SearchFilter
# from django_filters.rest_framework import DjangoFilterBackend

# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi

# # ---
# # Параметры Swagger для Оправ
# # ---
# frame_params = [
#     openapi.Parameter('brand', openapi.IN_QUERY,
#                       description="ID Бренда или список ID (напр. ?brand=1 или ?brand=1,3,5)", type=openapi.TYPE_STRING),
#     openapi.Parameter('material', openapi.IN_QUERY,
#                       description="ID Материала или список ID (напр. ?material=1,2)", type=openapi.TYPE_STRING),
#     openapi.Parameter('shape', openapi.IN_QUERY,
#                       description="ID Формы или список ID", type=openapi.TYPE_STRING),
#     openapi.Parameter('type', openapi.IN_QUERY,
#                       description="ID Типа или список ID", type=openapi.TYPE_STRING),
#     openapi.Parameter('gender', openapi.IN_QUERY,
#                       description="ID Пола или список ID", type=openapi.TYPE_STRING),
#     openapi.Parameter('age_group', openapi.IN_QUERY,
#                       description="ID Возрастной группы или список ID", type=openapi.TYPE_STRING),
#     openapi.Parameter('colors', openapi.IN_QUERY,
#                       description="Название цвета или список (напр. ?colors=Черный,Золотой)", type=openapi.TYPE_STRING),
#     openapi.Parameter('price__gte', openapi.IN_QUERY,
#                       description="Цена 'больше или равна'", type=openapi.TYPE_NUMBER),
#     openapi.Parameter('price__lte', openapi.IN_QUERY,
#                       description="Цена 'меньше или равна'", type=openapi.TYPE_NUMBER),
#     openapi.Parameter('search', openapi.IN_QUERY,
#                       description="Поиск по Имени, Артикулу или Бренду", type=openapi.TYPE_STRING),
#     openapi.Parameter(
#         'page_size', openapi.IN_QUERY,
#         description="Кол-во элементов на странице (по умолч: 5, макс: 100)",
#         type=openapi.TYPE_INTEGER
#     )
# ]

# # ---
# # Параметры Swagger для Линз
# # ---
# lens_params = [
#     openapi.Parameter('series', openapi.IN_QUERY,
#                       description="ID Серии или список ID (напр. ?series=1 или ?series=1,2)", type=openapi.TYPE_STRING),
#     openapi.Parameter('sph', openapi.IN_QUERY,
#                       description="Значение Сферы или список (напр. ?sph=-1.25)", type=openapi.TYPE_STRING),
#     openapi.Parameter('cyl', openapi.IN_QUERY,
#                       description="Значение Цилиндра или список (напр. ?cyl=0.50)", type=openapi.TYPE_STRING),
#     openapi.Parameter('dia', openapi.IN_QUERY,
#                       description="Значение Диаметра или список (напр. ?dia=70)", type=openapi.TYPE_STRING),
#     openapi.Parameter('search', openapi.IN_QUERY,
#                       description="Поиск по Имени Серии или ID из 1С", type=openapi.TYPE_STRING),
#     openapi.Parameter(
#         'page_size', openapi.IN_QUERY,
#         description="Кол-во элементов на странице (по умолч: 5, макс: 100)",
#         type=openapi.TYPE_INTEGER
#     )
# ]


# class FrameListView(generics.ListAPIView):
#     queryset = Frame.objects.filter(stock__gt=0).distinct()
#     serializer_class = FrameSerializer
#     filterset_class = FrameFilter
#     permission_classes = [AllowAny]
#     filter_backends = (DjangoFilterBackend, SearchFilter)
#     search_fields = ('name', 'sku', 'brand__name')

#     @swagger_auto_schema(
#         tags=['Catalog (Каталог)'],
#         operation_summary="1. Получить список ОПРАВ (с фильтрами)",
#         manual_parameters=frame_params
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)


# class FrameFilterOptionsView(APIView):
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(
#         tags=['Catalog (Каталог)'],
#         operation_summary="2. Получить опции фильтров для ОПРАВ",
#         operation_description="Возвращает ВСЕ доступные Бренды, Материалы, Формы и т.д."
#     )
#     def get(self, request, *args, **kwargs):
#         # Получаем список групп цветов для фильтра
#         groups = ColorGroup.objects.all().order_by('order', 'name')

#         data = {
#             'brands': BrandSerializer(Brand.objects.all(), many=True).data,
#             'materials': FrameMaterialSerializer(FrameMaterial.objects.all(), many=True).data,
#             'shapes': FrameShapeSerializer(FrameShape.objects.all(), many=True).data,
#             'types': FrameTypeSerializer(FrameType.objects.all(), many=True).data,
#             'genders': FrameGenderSerializer(FrameGender.objects.all(), many=True).data,
#             'age_groups': FrameAgeGroupSerializer(FrameAgeGroup.objects.all(), many=True).data,
#             'colors': ColorGroupSerializer(groups, many=True).data
#         }
#         return Response(data)


# class LensListView(generics.ListAPIView):
#     queryset = Lens.objects.filter(stock__gt=0).select_related('series')
#     serializer_class = LensSerializer
#     filterset_class = LensFilter
#     permission_classes = [AllowAny]
#     filter_backends = (DjangoFilterBackend, SearchFilter)
#     search_fields = ('series__name', 'id_1c')

#     @swagger_auto_schema(
#         tags=['Catalog (Каталог)'],
#         operation_summary="3. Получить список ЛИНЗ (с фильтрами)",
#         manual_parameters=lens_params
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)


# class LensOptionsView(APIView):
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(
#         tags=['Catalog (Каталог)'],
#         operation_summary="4. Получить опции фильтров для ЛИНЗ",
#         operation_description="Возвращает доступные Серии, SPH, CYL и DIA, отфильтрованные по переданным параметрам."
#     )
#     def get(self, request, *args, **kwargs):
#         queryset = Lens.objects.filter(stock__gt=0)
#         sph = request.query_params.get('sph')
#         cyl = request.query_params.get('cyl')
#         dia = request.query_params.get('dia')

#         if sph:
#             queryset = queryset.filter(sph=sph)
#         if cyl:
#             queryset = queryset.filter(cyl=cyl)
#         if dia:
#             queryset = queryset.filter(dia=dia)

#         available_series_ids = queryset.values_list('series', flat=True).distinct()
#         available_series = LensSeries.objects.filter(id__in=available_series_ids).order_by('name')

#         series_data = LensSeriesSerializer(available_series, many=True).data
#         sph_values = queryset.values_list('sph', flat=True).distinct().order_by('sph')
#         cyl_values = queryset.values_list('cyl', flat=True).distinct().order_by('cyl')
#         dia_values = queryset.values_list('dia', flat=True).distinct().order_by('dia')

#         data = {
#             'series': series_data,
#             'sph': list(sph_values),
#             'cyl': list(cyl_values),
#             'dia': list(dia_values)
#         }
#         return Response(data)


# class ProductDetailView(APIView):
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(
#         tags=['Catalog (Каталог)'],
#         operation_summary="5. Получить продукт по типу и ID",
#         operation_description="product_type: frame или lens",
#     )
#     def get(self, request, product_type, pk, *args, **kwargs):
#         if product_type == 'frame':
#             try:
#                 product = Frame.objects.filter(stock__gt=0).get(pk=pk)
#             except Frame.DoesNotExist:
#                 return Response({"detail": "Продукт не найден."}, status=status.HTTP_404_NOT_FOUND)

#             return Response({
#                 "type": "frame",
#                 "item": FrameSerializer(product, context={"request": request}).data,
#             })

#         if product_type == 'lens':
#             try:
#                 product = Lens.objects.filter(stock__gt=0).select_related('series').get(pk=pk)
#             except Lens.DoesNotExist:
#                 return Response({"detail": "Продукт не найден."}, status=status.HTTP_404_NOT_FOUND)

#             return Response({
#                 "type": "lens",
#                 "item": LensSerializer(product, context={"request": request}).data,
#             })

#         return Response({"detail": "Неверный тип продукта."}, status=status.HTTP_404_NOT_FOUND)
from django.db.models import Case, IntegerField, Value, When
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Frame, Lens, LensSeries, Color, ColorGroup, Brand, FrameMaterial, FrameShape, FrameType, FrameGender, FrameAgeGroup, ProductColor
from .serializers import (
    FrameSerializer, LensSerializer, LensSeriesSerializer, ColorSerializer, ColorGroupSerializer,
    BrandSerializer, FrameMaterialSerializer, FrameShapeSerializer,
    FrameTypeSerializer, FrameGenderSerializer, FrameAgeGroupSerializer,
    ProductColorSerializer
)
from .filters import FrameFilter, LensFilter
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# ---
# Параметры Swagger для Оправ
# ---
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
    openapi.Parameter('colors', openapi.IN_QUERY,
                      description="Название цвета или список (напр. ?colors=Черный,Золотой)", type=openapi.TYPE_STRING),
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
# Параметры Swagger для Линз
# ---
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


class FrameListView(generics.ListAPIView):
    queryset = (
        Frame.objects.filter(stock__gt=0)
        .annotate(
            has_price=Case(
                When(price__gt=0, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by('has_price', 'id')
        .distinct()
    )
    serializer_class = FrameSerializer
    filterset_class = FrameFilter
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('name', 'sku', 'brand__name')

    @swagger_auto_schema(
        tags=['Catalog (Каталог)'],
        operation_summary="1. Получить список ОПРАВ (с фильтрами)",
        manual_parameters=frame_params
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FrameFilterOptionsView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Catalog (Каталог)'],
        operation_summary="2. Получить опции фильтров для ОПРАВ",
        operation_description="Возвращает ВСЕ доступные Бренды, Материалы, Формы и т.д."
    )
    def get(self, request, *args, **kwargs):
        # Возвращаем только те группы цветов, у которых есть оправы в наличии (stock > 0)
        active_group_ids = (
            Frame.objects.filter(stock__gt=0, colors__color__group__isnull=False)
            .values_list('colors__color__group_id', flat=True)
            .distinct()
        )
        groups = ColorGroup.objects.filter(id__in=active_group_ids).order_by('order', 'name')

        data = {
            'brands': BrandSerializer(Brand.objects.all(), many=True).data,
            'materials': FrameMaterialSerializer(FrameMaterial.objects.all(), many=True).data,
            'shapes': FrameShapeSerializer(FrameShape.objects.all(), many=True).data,
            'types': FrameTypeSerializer(FrameType.objects.all(), many=True).data,
            'genders': FrameGenderSerializer(FrameGender.objects.all(), many=True).data,
            'age_groups': FrameAgeGroupSerializer(FrameAgeGroup.objects.all(), many=True).data,
            'colors': ColorGroupSerializer(groups, many=True).data
        }
        return Response(data)


class LensListView(generics.ListAPIView):
    queryset = (
        Lens.objects.filter(stock__gt=0)
        .select_related('series')
        .annotate(
            has_price=Case(
                When(price__gt=0, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by('has_price', 'id')
    )
    serializer_class = LensSerializer
    filterset_class = LensFilter
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('series__name', 'name', 'sku', 'id_1c')

    @swagger_auto_schema(
        tags=['Catalog (Каталог)'],
        operation_summary="3. Получить список ЛИНЗ (с фильтрами)",
        manual_parameters=lens_params
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class LensOptionsView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Catalog (Каталог)'],
        operation_summary="4. Получить опции фильтров для ЛИНЗ",
        operation_description="Возвращает доступные Серии, SPH, CYL и DIA, отфильтрованные по переданным параметрам."
    )
    def get(self, request, *args, **kwargs):
        from decimal import Decimal, InvalidOperation

        queryset = Lens.objects.filter(stock__gt=0)
        sph_str = request.query_params.get('sph')
        cyl_str = request.query_params.get('cyl')
        dia_str = request.query_params.get('dia')

        u_sph = None
        if sph_str:
            try: u_sph = Decimal(sph_str)
            except InvalidOperation: pass

        u_cyl = None
        if cyl_str:
            try: u_cyl = Decimal(cyl_str)
            except InvalidOperation: pass

        u_dia = None
        if dia_str:
            try: u_dia = int(dia_str)
            except ValueError: pass

        if u_dia is not None:
            queryset = queryset.filter(dia=u_dia)

        sph_set = set()
        cyl_set = set()
        dia_set = set()
        series_set = set()

        for lens in queryset.values('sph', 'cyl', 'dia', 'series_id'):
            db_sph = lens['sph']
            db_cyl = lens['cyl']
            db_dia = lens['dia']
            db_series = lens['series_id']

            # Rep 1 (Original)
            rep1_sph = db_sph
            rep1_cyl = db_cyl
            rep1_match = True
            if u_sph is not None and u_sph != rep1_sph: rep1_match = False
            if u_cyl is not None and u_cyl != rep1_cyl: rep1_match = False

            # Rep 2 (Transposed)
            rep2_sph = db_sph + db_cyl
            rep2_cyl = -db_cyl
            rep2_match = True
            if u_sph is not None and u_sph != rep2_sph: rep2_match = False
            if u_cyl is not None and u_cyl != rep2_cyl: rep2_match = False

            if rep1_match:
                sph_set.add(rep1_sph)
                cyl_set.add(rep1_cyl)
                if db_dia is not None:
                    dia_set.add(db_dia)
                series_set.add(db_series)
                
            if rep2_match:
                sph_set.add(rep2_sph)
                cyl_set.add(rep2_cyl)
                if db_dia is not None:
                    dia_set.add(db_dia)
                series_set.add(db_series)

        available_series = LensSeries.objects.filter(id__in=series_set).order_by('name')
        series_data = LensSeriesSerializer(available_series, many=True).data

        data = {
            'series': series_data,
            'sph': sorted(list(sph_set)),
            'cyl': sorted(list(cyl_set)),
            'dia': sorted(list(dia_set))
        }
        return Response(data)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Catalog (Каталог)'],
        operation_summary="5. Получить продукт по типу и ID",
        operation_description="product_type: frame или lens",
    )
    def get(self, request, product_type, pk, *args, **kwargs):
        if product_type == 'frame':
            try:
                product = Frame.objects.filter(stock__gt=0).get(pk=pk)
            except Frame.DoesNotExist:
                return Response({"detail": "Продукт не найден."}, status=status.HTTP_404_NOT_FOUND)

            return Response({
                "type": "frame",
                "item": FrameSerializer(product, context={"request": request}).data,
            })

        if product_type == 'lens':
            try:
                product = Lens.objects.filter(stock__gt=0).select_related('series').get(pk=pk)
            except Lens.DoesNotExist:
                return Response({"detail": "Продукт не найден."}, status=status.HTTP_404_NOT_FOUND)

            return Response({
                "type": "lens",
                "item": LensSerializer(product, context={"request": request}).data,
            })

        return Response({"detail": "Неверный тип продукта."}, status=status.HTTP_404_NOT_FOUND)
