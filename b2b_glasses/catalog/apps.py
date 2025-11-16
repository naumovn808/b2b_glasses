from django.apps import AppConfig
import sys  # <--- Добавлен импорт sys


class CatalogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalog'

    def ready(self):
        """
        Этот метод вызывается, когда Django готов к работе.
        """
        # Мы должны запускать планировщик ТОЛЬКО когда
        # запускается основной сервер (runserver)
        # и НЕ запускать его, когда мы делаем 'migrate' или 'import_1c_xml'

        # Проверяем, что 'runserver' есть в аргументах запуска
        is_running_server = 'runserver' in sys.argv

        if is_running_server:
            # Импортируем наш планировщик
            from . import scheduler
            # Запускаем!
            scheduler.start()
