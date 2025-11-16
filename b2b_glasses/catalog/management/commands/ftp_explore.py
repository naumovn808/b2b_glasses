import ftplib
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

print("[DEBUG] Файл ftp_explore.py (v11 - OPTS UTF8 ON) ЗАГРУЖЕН.")


class Command(BaseCommand):
    help = 'Подключается к FTP, принудительно включает UTF-8 и печатает дерево.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            f'Подключаюсь к FTP: {settings.FTP_HOST}:{settings.FTP_PORT}...'))

        try:
            # 1. Подключаемся БЕЗ кодировки
            with ftplib.FTP() as ftp:
                ftp.connect(settings.FTP_HOST, settings.FTP_PORT)
                ftp.login(settings.FTP_USER, settings.FTP_PASS)

                # --- ГЛАВНОЕ ИСПРАВЛЕНИЕ ---
                # 2. Отправляем команду серверу: "Включи UTF-8"
                try:
                    ftp.sendcmd("OPTS UTF8 ON")
                    self.stdout.write(self.style.SUCCESS(
                        '...Сервер подтвердил команду "OPTS UTF8 ON".'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(
                        f'...Сервер не принял "OPTS UTF8 ON" ({e}), продолжаем с риском...'))

                # 3. Устанавливаем кодировку UTF-8 для этого соединения
                ftp.encoding = "utf-8"
                # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

                ftp.set_pasv(True)

                self.stdout.write(self.style.SUCCESS(
                    'Успешно подключен к FTP (в режиме UTF-8).'))
                self.stdout.write(self.style.WARNING(
                    '--- Структура папок (попытка v11) ---'))

                # 4. Запускаем рекурсивный обход
                self.list_ftp_dir(ftp, '/')

        except ftplib.error_perm as e:
            raise CommandError(f'Ошибка FTP (права доступа/пароль?): {e}')
        except Exception as e:
            raise CommandError(f'Ошибка FTP (адрес/порт?): {e}')

    def list_ftp_dir(self, ftp, path, indent_level=0):
        """
        Рекурсивно обходит FTP-папки и печатает их содержимое.
        (Использует nlst + cwd, как в v5)
        """
        indent = "  " * indent_level

        try:
            items = ftp.nlst(path)

            for item_name in items:
                # item_name теперь должен быть в UTF-8, напр. "Заказы"
                if item_name in ('.', '..'):
                    continue

                # item_name может быть полным путем, извлекаем только имя
                base_name = os.path.basename(item_name)

                try:
                    # Пытаемся "зайти" в папку
                    # ftp.cwd() теперь тоже работает с UTF-8
                    ftp.cwd(item_name)

                    self.stdout.write(f'{indent}+ {base_name}/')
                    # Рекурсивно "заходим" внутрь
                    self.list_ftp_dir(ftp, '.', indent_level + 1)
                    # Возвращаемся обратно
                    ftp.cwd('..')
                except ftplib.error_perm:
                    # Это файл
                    self.stdout.write(f'{indent}- {base_name}')

        except ftplib.error_perm as e:
            self.stdout.write(self.style.ERROR(
                f'{indent} ! Не удалось прочитать папку {path}: {e}'))
        except Exception:
            pass
