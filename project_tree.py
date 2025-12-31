import os
import sys


PREFIX_BRANCH = "├── "
PREFIX_LAST = "└── "
PREFIX_VERTICAL = "│   "
PREFIX_EMPTY = "    "


EXCLUDE_DIRS = {'.git', '__pycache__', 'venv',
                '.idea', '.vscode', 'node_modules', 'media', 'staticfiles'}
EXCLUDE_FILES = {'.DS_Store', 'project_tree.py'}


def generate_tree(dir_path, prefix="", is_last=True):
    """
    Рекурсивно сканирует директорию и генерирует иерархическое представление.
    """

    try:

        items = [
            item for item in os.listdir(dir_path)
            if item not in EXCLUDE_DIRS and not (os.path.isdir(os.path.join(dir_path, item)) and item.startswith('.'))
            and item not in EXCLUDE_FILES
        ]
        items.sort()
    except OSError as e:
        print(f"Ошибка при чтении каталога {dir_path}: {e}", file=sys.stderr)
        return

    pointers = [PREFIX_LAST] * len(items)
    if len(items) > 0:
        pointers[:-1] = [PREFIX_BRANCH] * (len(items) - 1)

    for i, item in enumerate(items):
        path = os.path.join(dir_path, item)
        pointer = pointers[i]

        print(f"{prefix}{pointer}{item}")

        if os.path.isdir(path):

            new_prefix = PREFIX_EMPTY if pointer == PREFIX_LAST else PREFIX_VERTICAL

            generate_tree(path, prefix + new_prefix, i == len(items) - 1)


def main():
    """
    Основная функция, запускающая сканирование из текущего каталога.
    """

    root_dir = os.path.abspath(os.path.dirname(__file__))

    print(os.path.basename(root_dir) + '/')

    generate_tree(root_dir)


if __name__ == "__main__":
    main()
