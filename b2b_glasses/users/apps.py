from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Имя должно совпадать с названием папки приложения или тем, как оно записано в INSTALLED_APPS
    name = 'users'
    verbose_name = "ПОЛЬЗОВАТЕЛИ"

    def ready(self):
        # Импортируем сигналы. Важно использовать имя приложения 'users'
        import users.signals
