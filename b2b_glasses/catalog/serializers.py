from rest_framework import serializers
from . import models

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Brand
        fields = ('id', 'name')

class FrameMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FrameMaterial
        fields = ('id', 'name')

class FrameShapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FrameShape
        fields = ('id', 'name')

class FrameTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FrameType
        fields = ('id', 'name')

class FrameGenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FrameGender
        fields = ('id', 'name')

class FrameAgeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FrameAgeGroup
        fields = ('id', 'name')

class ColorGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ColorGroup
        fields = ('id', 'name', 'hex_value')

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Color
        fields = ('id', 'name', 'hex_value')

class ProductColorSerializer(serializers.ModelSerializer):
    # Приоритет отдаем группе, если она есть
    name = serializers.SerializerMethodField()
    hex_value = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductColor
        fields = ('id', 'name', 'hex_value', 'order')

    def get_name(self, obj):
        if obj.color and obj.color.group:
            return obj.color.group.name
        return obj.color.name if obj.color else obj.name

    def get_hex_value(self, obj):
        if obj.color and obj.color.group:
            return obj.color.group.hex_value
        return obj.color.hex_value if obj.color else "#000000"

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductImage
        fields = ('id', 'image', 'order')

class FrameSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField()
    material = serializers.StringRelatedField()
    shape = serializers.StringRelatedField()
    type = serializers.StringRelatedField()
    gender = serializers.StringRelatedField()
    age_group = serializers.StringRelatedField()
    colors = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = models.Frame
        fields = (
            'id', 'id_1c', 'name', 'sku', 'brand', 'material', 'shape',
            'type', 'gender', 'age_group',
            'size_a', 'size_b', 'size_d', 'size_temple', 'price', 'stock',
            'colors', 'images',
        )

    def get_colors(self, obj):
        # Собираем уникальные группы цветов для этого товара
        # Чтобы в карточке не было трех черных кружков
        product_colors = obj.colors.all().select_related('color__group')
        unique_groups = {}
        
        for pc in product_colors:
            if pc.color and pc.color.group:
                g = pc.color.group
                unique_groups[g.id] = {
                    'id': g.id,
                    'name': g.name,
                    'hex_value': g.hex_value
                }
            else:
                # Если группы нет, выводим как есть (индивидуальный цвет)
                c_id = f"c_{pc.id}"
                unique_groups[c_id] = {
                    'id': pc.id,
                    'name': pc.color.name if pc.color else pc.name,
                    'hex_value': pc.color.hex_value if pc.color else "#000000"
                }
        
        return list(unique_groups.values())

class LensSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LensSeries
        fields = ('id', 'name')

class LensSerializer(serializers.ModelSerializer):
    series = serializers.StringRelatedField()
    colors = ProductColorSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = models.Lens
        fields = (
            'id', 'id_1c', 'name', 'sku', 'barcode', 'series',
            'sph', 'cyl', 'dia', 'price', 'stock',
            'colors', 'images',
        )
