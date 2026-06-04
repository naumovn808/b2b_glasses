# import django_filters
# from .models import Frame, Lens

# # --- 1. СОЗДАЕМ "УМНЫЙ" ФИЛЬТР ---
# # Он будет "наследником" BaseInFilter (который умеет
# # работать со списками, разделенными запятыми) и NumberFilter.


# class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
#     """
#     "Умный" фильтр: ищет по 'in' (список, разделенный запятыми)
#     но НЕ добавляет '__in' к названию в URL.
#     Он будет работать и для ?brand=1, и для ?brand=1,3,5
#     """
#     pass


# class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
#     """
#     Аналогичный фильтр для строк (например, для названий цветов)
#     """
#     pass

# # --- 2. ПРИМЕНЯЕМ ЕГО К ОПРАВАМ ---


# class FrameFilter(django_filters.FilterSet):
#     """
#     Набор фильтров для GET-запроса Оправ.
#     (Теперь использует "Умный" фильтр)
#     """
#     # Мы явно "говорим" Django, какой фильтр использовать
#     # и какое 'help_text' (объяснение) показать в Swagger.
#     brand = NumberInFilter(
#         field_name='brand_id',
#         lookup_expr='in',
#         help_text="ID Бренда или список ID (напр. ?brand=1 или ?brand=1,3,5)"
#     )
#     material = NumberInFilter(
#         field_name='material_id', lookup_expr='in',
#         help_text="ID Материала или список ID (напр. ?material=1,2)"
#     )
#     shape = NumberInFilter(
#         field_name='shape_id', lookup_expr='in',
#         help_text="ID Формы или список ID"
#     )
#     type = NumberInFilter(
#         field_name='type_id', lookup_expr='in',
#         help_text="ID Типа или список ID"
#     )
#     gender = NumberInFilter(
#         field_name='gender_id', lookup_expr='in',
#         help_text="ID Пола или список ID"
#     )
#     age_group = NumberInFilter(
#         field_name='age_group_id', lookup_expr='in',
#         help_text="ID Возрастной группы или список ID"
#     )

#     # Фильтр по цветам (по ID группы)
#     colors = NumberInFilter(
#         field_name='colors__color__group__id', lookup_expr='in',
#         help_text="ID группы цветов или список (напр. ?colors=1,7)"
#     )

#     # Фильтры по диапазону (остаются как есть)
#     price__gte = django_filters.NumberFilter(
#         field_name='price', lookup_expr='gte', help_text="Цена 'больше или равна'")
#     price__lte = django_filters.NumberFilter(
#         field_name='price', lookup_expr='lte', help_text="Цена 'меньше или равна'")

#     class Meta:
#         model = Frame
#         # 'stock__gt' мы используем по умолчанию в View
#         fields = [
#             'brand', 'material', 'shape', 'type', 'gender', 'age_group',
#             'price__gte', 'price__lte'
#         ]

# # --- 3. ПРИМЕНЯЕМ ЕГО К ЛИНЗАМ (ГЛАВНЫЙ ФИКС) ---


# class LensFilter(django_filters.FilterSet):
#     """
#     Набор фильтров для GET-запроса Линз.
#     (Теперь тоже "Умный")
#     """
#     series = NumberInFilter(
#         field_name='series_id', lookup_expr='in',
#         help_text="ID Серии или список ID (напр. ?series=1 или ?series=1,2)"
#     )
#     # --- ИСПРАВЛЕНО: 'sph' и 'cyl' теперь NumberInFilter ---
#     sph = NumberInFilter(
#         field_name='sph', lookup_expr='in',
#         help_text="Значение Сферы или список (напр. ?sph=-1.25 или ?sph=-1.25,-1.50)"
#     )
#     cyl = NumberInFilter(
#         field_name='cyl', lookup_expr='in',
#         help_text="Значение Цилиндра или список (напр. ?cyl=0.50 или ?cyl=0.50,0.75)"
#     )
#     # ---
#     dia = NumberInFilter(
#         field_name='dia', lookup_expr='in',
#         help_text="Значение Диаметра или список (напр. ?dia=70 или ?dia=65,70)"
#     )

#     class Meta:
#         model = Lens
#         fields = ['series', 'sph', 'cyl', 'dia']
import django_filters
from django.db.models import F, Q
from decimal import Decimal, InvalidOperation
from .models import Frame, Lens

# --- 1. СОЗДАЕМ "УМНЫЙ" ФИЛЬТР ---
# Он будет "наследником" BaseInFilter (который умеет
# работать со списками, разделенными запятыми) и NumberFilter.


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """
    "Умный" фильтр: ищет по 'in' (список, разделенный запятыми)
    но НЕ добавляет '__in' к названию в URL.
    Он будет работать и для ?brand=1, и для ?brand=1,3,5
    """
    pass


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    """
    Аналогичный фильтр для строк (например, для названий цветов)
    """
    pass

# --- 2. ПРИМЕНЯЕМ ЕГО К ОПРАВАМ ---


class FrameFilter(django_filters.FilterSet):
    """
    Набор фильтров для GET-запроса Оправ.
    (Теперь использует "Умный" фильтр)
    """
    # Мы явно "говорим" Django, какой фильтр использовать
    # и какое 'help_text' (объяснение) показать в Swagger.
    brand = NumberInFilter(
        field_name='brand_id',
        lookup_expr='in',
        help_text="ID Бренда или список ID (напр. ?brand=1 или ?brand=1,3,5)"
    )
    material = NumberInFilter(
        field_name='material_id', lookup_expr='in',
        help_text="ID Материала или список ID (напр. ?material=1,2)"
    )
    shape = NumberInFilter(
        field_name='shape_id', lookup_expr='in',
        help_text="ID Формы или список ID"
    )
    type = NumberInFilter(
        field_name='type_id', lookup_expr='in',
        help_text="ID Типа или список ID"
    )
    gender = NumberInFilter(
        field_name='gender_id', lookup_expr='in',
        help_text="ID Пола или список ID"
    )
    age_group = NumberInFilter(
        field_name='age_group_id', lookup_expr='in',
        help_text="ID Возрастной группы или список ID"
    )

    # Фильтр по цветам (по ID группы)
    colors = NumberInFilter(
        field_name='colors__color__group__id', lookup_expr='in',
        help_text="ID группы цветов или список (напр. ?colors=1,7)"
    )

    # Фильтры по диапазону (остаются как есть)
    price__gte = django_filters.NumberFilter(
        field_name='price', lookup_expr='gte', help_text="Цена 'больше или равна'")
    price__lte = django_filters.NumberFilter(
        field_name='price', lookup_expr='lte', help_text="Цена 'меньше или равна'")

    class Meta:
        model = Frame
        # 'stock__gt' мы используем по умолчанию в View
        fields = [
            'brand', 'material', 'shape', 'type', 'gender', 'age_group',
            'price__gte', 'price__lte'
        ]

# --- 3. ПРИМЕНЯЕМ ЕГО К ЛИНЗАМ (ГЛАВНЫЙ ФИКС) ---


class LensFilter(django_filters.FilterSet):
    """
    Набор фильтров для GET-запроса Линз.
    (Теперь тоже "Умный")
    """
    series = NumberInFilter(
        field_name='series_id', lookup_expr='in',
        help_text="ID Серии или список ID (напр. ?series=1 или ?series=1,2)"
    )
    # --- ИСПРАВЛЕНО: 'sph' и 'cyl' теперь NumberInFilter ---
    sph = NumberInFilter(
        field_name='sph', lookup_expr='in',
        help_text="Значение Сферы или список (напр. ?sph=-1.25 или ?sph=-1.25,-1.50)"
    )
    cyl = NumberInFilter(
        field_name='cyl', lookup_expr='in',
        help_text="Значение Цилиндра или список (напр. ?cyl=0.50 или ?cyl=0.50,0.75)"
    )
    # ---
    dia = NumberInFilter(
        field_name='dia', lookup_expr='in',
        help_text="Значение Диаметра или список (напр. ?dia=70 или ?dia=65,70)"
    )

    class Meta:
        model = Lens
        fields = ['series', 'sph', 'cyl', 'dia']

    def filter_queryset(self, queryset):
        for name, value in self.form.cleaned_data.items():
            if name in ['sph', 'cyl'] or value in (None, [], ''):
                continue
            queryset = self.filters[name].filter(queryset, value)

        sph_values = self.form.cleaned_data.get('sph') or []
        cyl_values = self.form.cleaned_data.get('cyl') or []

        if sph_values or cyl_values:
            queryset = queryset.annotate(
                transposed_sph=F('sph') + F('cyl'),
                transposed_cyl=-F('cyl')
            )
            
            q_objects = Q()
            if sph_values and cyl_values:
                for s in sph_values:
                    for c in cyl_values:
                        try:
                            s_dec = Decimal(str(s))
                            c_dec = Decimal(str(c))
                            q_orig = Q(sph=s_dec, cyl=c_dec)
                            q_trans = Q(transposed_sph=s_dec, transposed_cyl=c_dec)
                            q_objects |= (q_orig | q_trans)
                        except (InvalidOperation, ValueError):
                            pass
            elif sph_values:
                for s in sph_values:
                    try:
                        s_dec = Decimal(str(s))
                        q_orig = Q(sph=s_dec)
                        q_trans = Q(transposed_sph=s_dec)
                        q_objects |= (q_orig | q_trans)
                    except (InvalidOperation, ValueError):
                        pass
            elif cyl_values:
                for c in cyl_values:
                    try:
                        c_dec = Decimal(str(c))
                        q_orig = Q(cyl=c_dec)
                        q_trans = Q(transposed_cyl=c_dec)
                        q_objects |= (q_orig | q_trans)
                    except (InvalidOperation, ValueError):
                        pass
                        
            if q_objects:
                queryset = queryset.filter(q_objects)
            else:
                queryset = queryset.none()
                
        return queryset
