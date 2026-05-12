import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'b2b_glasses.settings')
django.setup()

from catalog.models import Color, ColorGroup

def run():
    # Создаем группу "Другое"
    other, _ = ColorGroup.objects.get_or_create(
        name='Другое', 
        defaults={'hex_value': '#808080', 'order': 100}
    )

    mapping = {
        'черн': 'Черный', 'black': 'Черный',
        'бел': 'Белый', 'white': 'Белый',
        'золот': 'Золотой', 'gold': 'Золотой',
        'серебр': 'Серебряный', 'silver': 'Серебряный',
        'красн': 'Красный', 'red': 'Красный',
        'син': 'Синий', 'blue': 'Синий',
        'голуб': 'Синий',
        'зелен': 'Зеленый', 'green': 'Зеленый',
        'коричн': 'Коричневый', 'brown': 'Коричневый',
        'сер': 'Серый', 'grey': 'Серый', 'gray': 'Серый',
        'розов': 'Розовый', 'pink': 'Розовый',
        'прозрач': 'Прозрачный', 'crystal': 'Прозрачный',
        'беж': 'Бежевый', 'beige': 'Бежевый',
        'желт': 'Золотой', 'yellow': 'Золотой',
        'фиолет': 'Розовый', 'purple': 'Розовый'
    }

    colors = Color.objects.all()
    count = 0
    other_count = 0

    for c in colors:
        name = c.name.lower()
        assigned = False
        for key, group_name in mapping.items():
            if key in name:
                group = ColorGroup.objects.filter(name=group_name).first()
                if group:
                    c.group = group
                    c.save()
                    assigned = True
                    count += 1
                    break
        
        if not assigned:
            c.group = other
            c.save()
            other_count += 1

    print(f"Successfully grouped {count} colors.")
    print(f"Moved {other_count} colors to 'Other' group.")

if __name__ == '__main__':
    run()
