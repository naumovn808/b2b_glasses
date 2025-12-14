from django.db import models
from django.utils import timezone
from solo.models import SingletonModel
from ckeditor.fields import RichTextField


class Contacts(SingletonModel):
    phone = models.CharField("Телефон", max_length=50)
    email = models.EmailField("Email")
    address_label = models.CharField("Адрес (название)", max_length=255)
    address_link = models.URLField("Ссылка на карту", blank=True, null=True)
    work_hours = models.CharField("Время работы", max_length=255)

    def __str__(self):
        return "Контакты"

    class Meta:
        verbose_name = "Контакты"


class AboutUs(SingletonModel):
    text = RichTextField("Текст 'О нас'")

    def __str__(self):
        return "О нас"

    class Meta:
        verbose_name = "Блок 'О нас'"


class Certificate(models.Model):
    about_us = models.ForeignKey(
        AboutUs, related_name='certificates', on_delete=models.CASCADE)
    title = models.CharField("Название сертификата",
                             max_length=255, blank=True)
    image = models.ImageField("Изображение", upload_to='certificates/')

    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"


class Partner(models.Model):
    about_us = models.ForeignKey(
        AboutUs, related_name='partners', on_delete=models.CASCADE)
    name = models.CharField("Название партнера", max_length=255, blank=True)
    image = models.ImageField("Логотип", upload_to='partners/')
    link = models.URLField("Ссылка", blank=True, null=True)

    class Meta:
        verbose_name = "Партнёр"
        verbose_name_plural = "Партнёры"


class Training(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    image = models.ImageField("Изображение", upload_to='training/')
    description = RichTextField("Описание")
    order = models.PositiveIntegerField("Порядок отображения", default=0)

    class Meta:
        verbose_name = "Обучение"
        verbose_name_plural = "Обучение"
        ordering = ['order']


class FAQ(models.Model):
    question = models.CharField("Вопрос", max_length=500)
    answer = models.TextField("Ответ")
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Частый вопрос (FAQ)"
        verbose_name_plural = "Частые вопросы (FAQ)"
        ordering = ['order']


class News(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    image = models.ImageField("Изображение", upload_to='news/')
    text = RichTextField("Текст новости")
    created_at = models.DateTimeField("Дата публикации", default=timezone.now)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-created_at']
