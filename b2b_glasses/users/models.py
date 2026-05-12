from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid


class Company(models.Model):
    name = models.CharField(max_length=255)
    external_id = models.CharField(
        max_length=255, blank=True, null=True, unique=True, verbose_name="Внешний ID"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self):
        return self.name


class User(AbstractUser):
    username_validator = RegexValidator(
        r"^[\w.@+-]+$",
        "Введите правильное имя пользователя. Оно может содержать только буквы, цифры и знаки @/./+/-/_.",
        "invalid",
    )
    username = models.CharField(
        "Имя пользователя",
        max_length=150,
        unique=True,
        help_text="Обязательное поле. 150 символов или меньше. Допускаются любые символы.",
        error_messages={
            "unique": "Пользователь с таким именем уже существует.",
        },
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Компания",
    )

    telegram_id = models.BigIntegerField(
        unique=True, null=True, blank=True, verbose_name="Telegram ID"
    )
    telegram_username = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="Telegram Username"
    )
    telegram_first_name = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="Telegram First Name"
    )
    telegram_last_name = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="Telegram Last Name"
    )
    phone_number = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Номер телефона"
    )

    email = models.EmailField("Email", blank=True, null=True)
    first_name = models.CharField("Имя", max_length=150, blank=True, null=True)
    last_name = models.CharField("Фамилия", max_length=150, blank=True, null=True)

    def __str__(self):
        return self.username


class TelegramLinkToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Токен доступа (Telegram)"
        verbose_name_plural = "Токены доступа (Telegram)"

    def __str__(self):
        return f"Токен для {self.user.username}"
