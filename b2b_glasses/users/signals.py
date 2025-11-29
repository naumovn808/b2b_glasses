from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, TelegramLinkToken

@receiver(post_save, sender=User)
def create_telegram_token(sender, instance, created, **kwargs):
    """
    Автоматически создает TelegramLinkToken при создании нового пользователя.
    Срабатывает при создании через админку, инлайны, API или консоль.
    """
    if created:
        # Если у пользователя еще нет telegram_id, создаем токен для привязки
        if not instance.telegram_id:
            TelegramLinkToken.objects.get_or_create(user=instance)