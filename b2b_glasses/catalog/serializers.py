from rest_framework import serializers
from . import models

# --- Сериализаторы для ОПРАВ (уже были) ---


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Brand
        fields = ('id', 'name')
# ... (и все остальные FrameMaterialSerializer, FrameShapeSerializer и т.д.) ...


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


class FrameSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField()
    material = serializers.StringRelatedField()
    shape = serializers.StringRelatedField()
    type = serializers.StringRelatedField()
    gender = serializers.StringRelatedField()
    age_group = serializers.StringRelatedField()

    class Meta:
        model = models.Frame
        fields = (
            'id', 'id_1c', 'name', 'sku', 'brand', 'material', 'shape',
            'type', 'gender', 'age_group', 'color_code', 'color_name',
            'size_a', 'size_b', 'size_d', 'size_temple', 'price', 'stock'
        )

# --- ДОБАВЬТЕ ЭТИ КЛАССЫ В КОНЕЦ ФАЙЛА ---


class LensSeriesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка Серий Линз (Шаг 1 фильтра)
    """
    class Meta:
        model = models.LensSeries
        fields = ('id', 'name')


class LensSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка Линз (Результат фильтра)
    """
    series = serializers.StringRelatedField()

    class Meta:
        model = models.Lens
        fields = (
            'id', 'id_1c', 'series', 'sph', 'cyl', 'dia', 'price', 'stock'
        )
