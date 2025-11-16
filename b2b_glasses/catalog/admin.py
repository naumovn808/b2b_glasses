from django.contrib import admin
from . import models

# --- Регистрируем Справочники (Фильтры) ---
admin.site.register(models.Brand)
admin.site.register(models.FrameMaterial)
admin.site.register(models.FrameShape)
admin.site.register(models.FrameType)
admin.site.register(models.FrameGender)
admin.site.register(models.FrameAgeGroup)
admin.site.register(models.LensSeries)

# --- Настраиваем админку для Оправ ---


@admin.register(models.Frame)
class FrameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sku', 'brand', 'price', 'stock')
    list_filter = ('brand', 'material', 'shape', 'gender', 'age_group')
    search_fields = ('name', 'sku', 'id_1c')

# --- Настраиваем админку для Линз ---


@admin.register(models.Lens)
class LensAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_1c', 'series', 'sph',
                    'cyl', 'dia', 'price', 'stock')
    list_filter = ('series', 'sph', 'cyl', 'dia')
    search_fields = ('id_1c', 'series__name')
