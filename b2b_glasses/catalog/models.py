from django.db import models
import uuid  # <--- 1. Добавляем импорт для UUID

# --- (Все модели-фильтры Brand, FrameMaterial и т.д. остаются БЕЗ ИЗМЕНЕНИЙ) ---


class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True,
                            verbose_name="Название")

    def __str__(self): return self.name


class FrameMaterial(models.Model):
    name = models.CharField(max_length=255, unique=True,
                            verbose_name="Название")

    def __str__(self): return self.name


class FrameShape(models.Model):
    name = models.CharField(max_length=255, unique=True,
                            verbose_name="Название")

    def __str__(self): return self.name


class FrameType(models.Model):
    name = models.CharField(max_length=255, unique=True,
                            verbose_name="Название")

    def __str__(self): return self.name


class FrameGender(models.Model):
    name = models.CharField(max_length=100, unique=True,
                            verbose_name="Название")

    def __str__(self): return self.name


class FrameAgeGroup(models.Model):
    name = models.CharField(max_length=100, unique=True,
                            verbose_name="Название")

    def __str__(self): return self.name

# --- ОСНОВНАЯ МОДЕЛЬ ОПРАВЫ ---


class Frame(models.Model):
    id_1c = models.CharField(max_length=100, unique=True,
                             db_index=True, verbose_name="Ид из 1С")
    name = models.CharField(max_length=500, verbose_name="Наименование")
    sku = models.CharField(max_length=255, db_index=True,
                           verbose_name="Артикул")
    barcode = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Штрихкод")
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True)
    material = models.ForeignKey(
        FrameMaterial, on_delete=models.SET_NULL, null=True, blank=True)
    shape = models.ForeignKey(
        FrameShape, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.ForeignKey(
        FrameType, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.ForeignKey(
        FrameGender, on_delete=models.SET_NULL, null=True, blank=True)
    age_group = models.ForeignKey(
        FrameAgeGroup, on_delete=models.SET_NULL, null=True, blank=True)
    color_code = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Код цвета")
    color_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Название цвета")
    size_a = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Размер А")
    size_b = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Размер B")
    size_d = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Размер D (Мост)")
    size_temple = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Размер Заушника")

    price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Цена")
    stock = models.PositiveIntegerField(default=0, verbose_name="Остаток")

    # --- 2. ДОБАВЛЕНО ПОЛЕ ДЛЯ "ПОДМЕНЫ" ---
    run_id = models.UUIDField(
        default=uuid.uuid4, db_index=True, verbose_name="ID сессии импорта")

    def __str__(self):
        return self.name

# --- МОДЕЛИ ДЛЯ ЛИНЗ ---


class LensSeries(models.Model):
    name = models.CharField(max_length=500, unique=True,
                            verbose_name="Название серии")

    def __str__(self): return self.name


class Lens(models.Model):
    id_1c = models.CharField(max_length=100, unique=True,
                             db_index=True, verbose_name="Ид из 1С")
    series = models.ForeignKey(
        LensSeries, on_delete=models.CASCADE, verbose_name="Серия")

    sph = models.DecimalField(
        max_digits=5, decimal_places=2, db_index=True, verbose_name="Сфера (SPH)")
    cyl = models.DecimalField(
        max_digits=5, decimal_places=2, db_index=True, verbose_name="Цилиндр (CYL)")
    dia = models.IntegerField(db_index=True, verbose_name="Диаметр (DIA)")

    price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Цена")
    stock = models.PositiveIntegerField(default=0, verbose_name="Остаток")

    # --- 2. ДОБАВЛЕНО ПОЛЕ ДЛЯ "ПОДМЕНЫ" ---
    run_id = models.UUIDField(
        default=uuid.uuid4, db_index=True, verbose_name="ID сессии импорта")

    def __str__(self):
        return f"{self.series.name} (SPH: {self.sph} CYL: {self.cyl} DIA: {self.dia})"
