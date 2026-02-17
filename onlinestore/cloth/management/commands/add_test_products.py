from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from ...models import (
    Product, Category, Size, Color, Gender,
    ProductVariant, ProductImage, Role, User
)
import os
import random


class Command(BaseCommand):
    help = 'Add test products to database'

    def handle(self, *args, **options):
        self.stdout.write('Adding test products...')

        # Проверяем наличие медиа-файлов
        media_path = settings.MEDIA_ROOT / 'products'
        if not media_path.exists():
            self.stdout.write(self.style.ERROR('Media folder not found!'))
            return

        # Получаем или создаем категории
        categories = [
            {'name': 'Джинсы', 'slug': 'jeans'},
            {'name': 'Футболки', 'slug': 't-shirts'},
            {'name': 'Платья', 'slug': 'dresses'},
            {'name': 'Верхняя одежда', 'slug': 'outerwear'},
            {'name': 'Свитеры', 'slug': 'sweaters'},
        ]

        category_objects = []
        for cat_data in categories:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            category_objects.append(cat)
            self.stdout.write(f'Category: {cat.name}')

        # Получаем размеры
        sizes = Size.objects.all()
        if not sizes:
            self.stdout.write(self.style.ERROR('Sizes not found! Run init_data first'))
            return

        # Получаем цвета
        colors = Color.objects.all()
        if not colors:
            self.stdout.write(self.style.ERROR('Colors not found! Run init_data first'))
            return

        # Получаем пол
        genders = Gender.objects.all()

        # Список тестовых товаров
        test_products = [
            {
                'name': 'Классические джинсы',
                'slug': 'classic-jeans',
                'description': 'Классические джинсы из высококачественного денима. Идеально подходят для повседневной носки. Материал: 98% хлопок, 2% эластан.',
                'price': 3990,
                'material': '98% хлопок, 2% эластан',
                'care_instructions': 'Стирка при 30°C, не отбеливать, гладить при средней температуре',
                'category': 'jeans',
                'gender': 'unisex',
                'image': 'djins.png',
                'is_new': True,
                'is_bestseller': True,
            },
            {
                'name': 'Базовая футболка',
                'slug': 'basic-t-shirt',
                'description': 'Базовая футболка из 100% хлопка. Мягкая и комфортная, подходит для любого образа.',
                'price': 1490,
                'material': '100% хлопок',
                'care_instructions': 'Стирка при 30°C, не отбеливать',
                'category': 't-shirts',
                'gender': 'unisex',
                'image': 'futbolka.png',
                'is_new': True,
                'is_bestseller': False,
            },
            {
                'name': 'Джинсы с высокой талией',
                'slug': 'high-waist-jeans',
                'description': 'Модные джинсы с высокой талией. Подчеркивают фигуру и создают стильный силуэт.',
                'price': 4590,
                'material': '100% хлопок',
                'care_instructions': 'Стирка при 30°C, не отбеливать',
                'category': 'jeans',
                'gender': 'women',
                'image': 'djins.png',
                'is_new': True,
                'is_bestseller': False,
            },
            {
                'name': 'Оверсайз футболка',
                'slug': 'oversize-t-shirt',
                'description': 'Модная футболка оверсайз кроя. Свободная и комфортная, подходит для создания casual образов.',
                'price': 1890,
                'material': '100% хлопок',
                'care_instructions': 'Стирка при 30°C, не отбеливать',
                'category': 't-shirts',
                'gender': 'unisex',
                'image': 'futbolka.png',
                'is_new': False,
                'is_bestseller': True,
            },
        ]

        # Создаем товары
        for product_data in test_products:
            # Получаем категорию
            category = Category.objects.get(slug=product_data['category'])

            # Получаем пол
            gender = None
            if product_data['gender']:
                gender = Gender.objects.filter(name=product_data['gender']).first()

            # Создаем или получаем товар
            product, created = Product.objects.get_or_create(
                slug=product_data['slug'],
                defaults={
                    'name': product_data['name'],
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'category': category,
                    'gender': gender,
                    'material': product_data['material'],
                    'care_instructions': product_data['care_instructions'],
                    'is_new': product_data['is_new'],
                    'is_bestseller': product_data['is_bestseller'],
                }
            )

            if created:
                self.stdout.write(f'Created product: {product.name}')

                # Добавляем изображение
                image_path = media_path / product_data['image']
                if image_path.exists():
                    with open(image_path, 'rb') as f:
                        product_image = ProductImage.objects.create(
                            product=product,
                            image=File(f, name=product_data['image']),
                            is_main=True
                        )

                # Создаем варианты товара (разные размеры)
                for size in sizes:
                    # Случайное количество на складе
                    stock = random.randint(5, 20)

                    # Случайная цена (может немного отличаться от базовой)
                    price_variant = product.price * random.uniform(0.95, 1.05)

                    # Случайный цвет
                    color = random.choice(colors)

                    ProductVariant.objects.create(
                        product=product,
                        size=size,
                        color=color,
                        price=round(price_variant, -1),  # Округляем до десятков
                        stock_quantity=stock
                    )

                self.stdout.write(f'  Created {sizes.count()} variants')
            else:
                self.stdout.write(f'Product already exists: {product.name}')

        self.stdout.write(self.style.SUCCESS('Test products added successfully!'))