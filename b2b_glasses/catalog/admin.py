from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from . import models

# --- Регистрируем Справочники (Фильтры) ---
admin.site.register(models.Brand)
admin.site.register(models.FrameMaterial)
admin.site.register(models.FrameShape)
admin.site.register(models.FrameType)
admin.site.register(models.FrameGender)
admin.site.register(models.FrameAgeGroup)
admin.site.register(models.LensSeries)

@admin.register(models.ColorGroup)
class ColorGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_value', 'order')
    list_editable = ('hex_value', 'order')
    search_fields = ('name',)

@admin.register(models.Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'hex_value')
    list_editable = ('group', 'hex_value')
    list_filter = ('group',)
    search_fields = ('name',)

@admin.register(models.ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'color', 'name')
    list_filter = ('color__group',)
    search_fields = ('name', 'product__name')

class ProductColorInline(GenericTabularInline):
    model = models.ProductColor
    extra = 1
    fields = ('color', 'name', 'order')

class ProductImageInline(GenericTabularInline):
    model = models.ProductImage
    extra = 1
    fields = ('image', 'order')

# --- Настраиваем админку для Оправ ---

@admin.register(models.Frame)
class FrameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sku', 'brand', 'price', 'stock')
    list_filter = ('brand', 'material', 'shape', 'gender', 'age_group')
    search_fields = ('name', 'sku', 'id_1c')
    inlines = (ProductColorInline, ProductImageInline)

# --- Настраиваем админку для Линз ---

@admin.register(models.Lens)
class LensAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_1c', 'series', 'sph',
                    'cyl', 'dia', 'price', 'stock')
    list_filter = ('series', 'sph', 'cyl', 'dia')
    search_fields = ('id_1c', 'series__name')
    inlines = (ProductColorInline, ProductImageInline)
