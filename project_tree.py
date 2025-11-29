import os
import sys

# Определяем символы для построения дерева
PREFIX_BRANCH = "├── "
PREFIX_LAST = "└── "
PREFIX_VERTICAL = "│   "
PREFIX_EMPTY = "    "

# Список папок и файлов, которые нужно игнорировать
# Добавьте сюда любые другие папки, которые не должны отображаться (например, ваша venv)
EXCLUDE_DIRS = {'.git', '__pycache__', 'venv',
                '.idea', '.vscode', 'node_modules', 'media', 'staticfiles'}
EXCLUDE_FILES = {'.DS_Store', 'project_tree.py'}  # Игнорируем сам скрипт


def generate_tree(dir_path, prefix="", is_last=True):
    """
    Рекурсивно сканирует директорию и генерирует иерархическое представление.
    """

    # 1. Получаем содержимое каталога
    try:
        # Исключаем нежелательные папки и файлы
        items = [
            item for item in os.listdir(dir_path)
            if item not in EXCLUDE_DIRS and not (os.path.isdir(os.path.join(dir_path, item)) and item.startswith('.'))
            and item not in EXCLUDE_FILES
        ]
        items.sort()  # Сортируем для более чистого вывода
    except OSError as e:
        print(f"Ошибка при чтении каталога {dir_path}: {e}", file=sys.stderr)
        return

    # 2. Итерируемся по содержимому
    pointers = [PREFIX_LAST] * len(items)
    if len(items) > 0:
        pointers[:-1] = [PREFIX_BRANCH] * (len(items) - 1)

    for i, item in enumerate(items):
        path = os.path.join(dir_path, item)
        pointer = pointers[i]

        # 3. Выводим текущий элемент
        print(f"{prefix}{pointer}{item}")

        # 4. Если это папка, делаем рекурсивный вызов
        if os.path.isdir(path):

            # Определяем новый префикс для дочерних элементов
            new_prefix = PREFIX_EMPTY if pointer == PREFIX_LAST else PREFIX_VERTICAL

            generate_tree(path, prefix + new_prefix, i == len(items) - 1)


def main():
    """
    Основная функция, запускающая сканирование из текущего каталога.
    """
    # Текущий каталог (корень проекта)
    root_dir = os.path.abspath(os.path.dirname(__file__))

    # Выводим название проекта
    print(os.path.basename(root_dir) + '/')

    # Запускаем рекурсивное сканирование
    generate_tree(root_dir)


if __name__ == "__main__":
    main()
