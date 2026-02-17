from django.core.management.base import BaseCommand
from ...models import Category, Product, ProductVariant, Size, Color
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Создает тестовые товары для каждой категории'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Создание тестовых товаров...'))

        # Создаем размеры если их нет
        sizes_data = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '40', '42', '44', '46', '48', '50']
        sizes = {}
        for size_name in sizes_data:
            size, created = Size.objects.get_or_create(name=size_name)
            sizes[size_name] = size
            if created:
                self.stdout.write(f'  Создан размер: {size_name}')

        # Создаем цвета если их нет
        colors_data = [
            ('Черный', '#000000'),
            ('Белый', '#FFFFFF'),
            ('Серый', '#808080'),
            ('Бежевый', '#F5F5DC'),
            ('Синий', '#0000FF'),
            ('Красный', '#FF0000'),
            ('Зеленый', '#008000'),
            ('Коричневый', '#8B4513'),
        ]
        colors = {}
        for color_name, color_code in colors_data:
            color, created = Color.objects.get_or_create(
                name=color_name,
                defaults={'hex_code': color_code}
            )
            colors[color_name] = color
            if created:
                self.stdout.write(f'  Создан цвет: {color_name}')

        # Получаем все категории
        categories = Category.objects.all()

        if not categories.exists():
            self.stdout.write(self.style.ERROR('Нет категорий! Сначала создайте категории через админ-панель.'))
            return

        # Шаблоны товаров для разных категорий
        product_templates = {
            'футболк': [
                {'name': 'Базовая футболка', 'price': 1500, 'sizes': ['XS', 'S', 'M', 'L', 'XL'],
                 'material': '100% хлопок', 'description': 'Классическая базовая футболка из мягкого хлопка'},
                {'name': 'Футболка с принтом', 'price': 1800, 'sizes': ['S', 'M', 'L', 'XL'],
                 'material': '95% хлопок, 5% эластан', 'description': 'Стильная футболка с оригинальным принтом'},
                {'name': 'Oversize футболка', 'price': 2200, 'sizes': ['M', 'L', 'XL', 'XXL'],
                 'material': '100% хлопок', 'description': 'Модная футболка свободного кроя'},
            ],
            'рубаш': [
                {'name': 'Классическая рубашка', 'price': 3500, 'sizes': ['40', '42', '44', '46', '48'],
                 'material': '100% хлопок', 'description': 'Элегантная классическая рубашка для офиса'},
                {'name': 'Льняная рубашка', 'price': 4200, 'sizes': ['42', '44', '46', '48', '50'],
                 'material': '100% лен', 'description': 'Легкая летняя рубашка из натурального льна'},
                {'name': 'Рубашка slim fit', 'price': 3800, 'sizes': ['40', '42', '44', '46'],
                 'material': '97% хлопок, 3% эластан', 'description': 'Приталенная рубашка современного кроя'},
            ],
            'джинс': [
                {'name': 'Джинсы Slim', 'price': 4500, 'sizes': ['40', '42', '44', '46', '48'],
                 'material': '98% хлопок, 2% эластан', 'description': 'Узкие джинсы с эластаном для комфорта'},
                {'name': 'Джинсы Regular', 'price': 4200, 'sizes': ['42', '44', '46', '48', '50'],
                 'material': '100% хлопок деним', 'description': 'Классические джинсы прямого кроя'},
                {'name': 'Джинсы Wide Leg', 'price': 5000, 'sizes': ['40', '42', '44', '46'],
                 'material': '100% органический хлопок', 'description': 'Модные джинсы широкого кроя'},
            ],
            'свитер': [
                {'name': 'Вязаный свитер', 'price': 5500, 'sizes': ['S', 'M', 'L', 'XL'],
                 'material': '50% шерсть, 50% акрил', 'description': 'Теплый вязаный свитер для холодной погоды'},
                {'name': 'Тонкий джемпер', 'price': 3800, 'sizes': ['XS', 'S', 'M', 'L', 'XL'],
                 'material': '100% мериносовая шерсть', 'description': 'Легкий джемпер из премиальной шерсти'},
                {'name': 'Водолазка', 'price': 3200, 'sizes': ['S', 'M', 'L', 'XL'],
                 'material': '95% хлопок, 5% эластан', 'description': 'Классическая водолазка на каждый день'},
            ],
            'куртк': [
                {'name': 'Джинсовая куртка', 'price': 7500, 'sizes': ['S', 'M', 'L', 'XL'],
                 'material': '100% хлопок деним', 'description': 'Стильная джинсовая куртка универсального стиля'},
                {'name': 'Ветровка', 'price': 6200, 'sizes': ['M', 'L', 'XL', 'XXL'],
                 'material': '100% полиэстер', 'description': 'Легкая непродуваемая ветровка для межсезонья'},
                {'name': 'Бомбер', 'price': 8500, 'sizes': ['S', 'M', 'L', 'XL'],
                 'material': '100% нейлон', 'description': 'Модная куртка-бомбер в спортивном стиле'},
            ],
            'плать': [
                {'name': 'Летнее платье', 'price': 4500, 'sizes': ['XS', 'S', 'M', 'L'],
                 'material': '100% вискоза', 'description': 'Легкое летнее платье для жаркой погоды'},
                {'name': 'Вечернее платье', 'price': 8900, 'sizes': ['S', 'M', 'L'],
                 'material': '95% полиэстер, 5% эластан',
                 'description': 'Элегантное вечернее платье для особых случаев'},
                {'name': 'Платье-рубашка', 'price': 5200, 'sizes': ['S', 'M', 'L', 'XL'],
                 'material': '100% хлопок', 'description': 'Универсальное платье-рубашка на каждый день'},
            ],
            'брюк': [
                {'name': 'Классические брюки', 'price': 4800, 'sizes': ['40', '42', '44', '46', '48'],
                 'material': '70% полиэстер, 30% вискоза', 'description': 'Элегантные брюки для офиса'},
                {'name': 'Чиносы', 'price': 3900, 'sizes': ['42', '44', '46', '48'],
                 'material': '98% хлопок, 2% эластан', 'description': 'Удобные повседневные чиносы'},
                {'name': 'Карго брюки', 'price': 4500, 'sizes': ['S', 'M', 'L', 'XL'],
                 'material': '100% хлопок', 'description': 'Практичные брюки в стиле карго с карманами'},
            ],
        }

        created_count = 0

        for category in categories:
            category_name_lower = category.name.lower()

            # Находим подходящий шаблон (гибкий поиск по части названия)
            template_key = None
            for key in product_templates.keys():
                if key in category_name_lower or category_name_lower.startswith(key):
                    template_key = key
                    break

            if not template_key:
                # Используем общий шаблон
                templates = [
                    {'name': f'{category.name} Premium', 'price': 5000, 'sizes': ['S', 'M', 'L', 'XL'],
                     'material': 'Премиум материалы', 'description': f'Качественное изделие категории {category.name}'},
                    {'name': f'{category.name} Classic', 'price': 4000, 'sizes': ['M', 'L', 'XL'],
                     'material': 'Натуральные материалы', 'description': f'Классическая модель {category.name}'},
                    {'name': f'{category.name} Modern', 'price': 4500, 'sizes': ['S', 'M', 'L'],
                     'material': 'Современные ткани', 'description': f'Модная модель {category.name}'},
                ]
            else:
                templates = product_templates[template_key]

            self.stdout.write(f'\nОбработка категории: {category.name}')

            for template in templates:
                for color_name in ['Черный', 'Белый', 'Серый', 'Бежевый']:
                    if color_name not in colors:
                        continue

                    # Создаем товар
                    product_name = f"{template['name']} {color_name}"

                    # Проверяем, не существует ли уже
                    if Product.objects.filter(name=product_name, category=category).exists():
                        self.stdout.write(f'  - Пропускаем (уже существует): {product_name}')
                        continue

                    try:
                        product = Product.objects.create(
                            category=category,
                            name=product_name,
                            description=template['description'],
                            price=Decimal(template['price']),
                            material=template.get('material', 'Натуральные материалы'),
                            care_instructions='Машинная стирка при 30°C, не отбеливать',
                            is_active=True,
                            is_new=random.choice([True, False]),
                        )

                        # Создаем варианты для каждого размера
                        variant_count = 0
                        for size_name in template['sizes']:
                            if size_name in sizes:
                                # Небольшая вариация цены в зависимости от размера
                                price_variation = Decimal(random.randint(-200, 300))
                                variant_price = Decimal(template['price']) + price_variation

                                ProductVariant.objects.create(
                                    product=product,
                                    size=sizes[size_name],
                                    color=colors[color_name],
                                    price=variant_price,
                                    stock_quantity=random.randint(5, 50),
                                )
                                variant_count += 1

                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f'  ✓ {product_name} ({variant_count} вариантов)'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ✗ Ошибка при создании {product_name}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\n{"=" * 60}'))
        self.stdout.write(self.style.SUCCESS(f'Готово! Создано товаров: {created_count}'))
        self.stdout.write(self.style.WARNING(f'{"=" * 60}'))
        self.stdout.write(self.style.WARNING('\n⚠ ВАЖНО: Изображения нужно добавить через админ-панель!'))
        self.stdout.write(
            self.style.WARNING('Перейдите в /admin/ → Products → выберите товар → добавьте изображения\n'))
