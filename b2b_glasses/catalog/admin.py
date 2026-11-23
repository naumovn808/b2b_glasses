from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html
from . import models

# --- Регистрируем Справочники (Фильтры) ---
admin.site.register(models.Brand)
admin.site.register(models.FrameMaterial)
admin.site.register(models.FrameShape)
admin.site.register(models.FrameType)
admin.site.register(models.FrameGender)
admin.site.register(models.FrameAgeGroup)
admin.site.register(models.LensSeries)


class ColorGroupAdminForm(forms.ModelForm):
    class Meta:
        model = models.ColorGroup
        fields = '__all__'
        widgets = {
            'hex_value': forms.TextInput(attrs={'type': 'color'}),
        }


class ColorAdminForm(forms.ModelForm):
    class Meta:
        model = models.Color
        fields = '__all__'
        widgets = {
            'hex_value': forms.TextInput(attrs={'type': 'color'}),
        }


@admin.register(models.ColorGroup)
class ColorGroupAdmin(admin.ModelAdmin):
    form = ColorGroupAdminForm
    list_display = ('name', 'color_preview', 'hex_value', 'order', 'active_frames_count')
    list_editable = ('hex_value', 'order')
    search_fields = ('name',)

    @admin.display(description="Цвет")
    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;border-radius:50%;'
            'background:{};border:1px solid #ccc;vertical-align:middle;"></span>',
            obj.hex_value,
        )

    @admin.display(description="Оправ в наличии")
    def active_frames_count(self, obj):
        return models.Frame.objects.filter(
            stock__gt=0, colors__color__group=obj
        ).distinct().count()


@admin.register(models.Color)
class ColorAdmin(admin.ModelAdmin):
    form = ColorAdminForm
    list_display = ('name', 'group', 'color_preview', 'hex_value')
    list_editable = ('group', 'hex_value')
    list_filter = ('group',)
    search_fields = ('name',)

    @admin.display(description="Цвет")
    def color_preview(self, obj):
        hex_val = obj.group.hex_value if obj.group else obj.hex_value
        return format_html(
            '<span style="display:inline-block;width:18px;height:18px;border-radius:50%;'
            'background:{};border:1px solid #ccc;vertical-align:middle;"></span>',
            hex_val,
        )


@admin.register(models.ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'color', 'name')
    list_filter = ('color__group',)
    search_fields = ('name', 'color__name')

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
    list_display = ('id', 'id_1c', 'name', 'series', 'sph',
                    'cyl', 'dia', 'price', 'stock')
    list_filter = ('series', 'sph', 'cyl', 'dia')
    search_fields = ('id_1c', 'name', 'sku', 'series__name')
    inlines = (ProductColorInline, ProductImageInline)
