from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ...models import (
    Role, OrderStatus, TransactionStatus, DeliveryMethod,
    Gender, Size, Color, Category
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize database with required data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing database...')

        # Создаем роли
        roles = ['user', 'moderator', 'admin']
        for role_name in roles:
            Role.objects.get_or_create(name=role_name)
            self.stdout.write(f'Created role: {role_name}')

        # Создаем статусы заказов
        statuses = ['created', 'paid', 'shipped', 'delivered', 'cancelled']
        for status_name in statuses:
            OrderStatus.objects.get_or_create(name=status_name)
            self.stdout.write(f'Created order status: {status_name}')

        # Создаем статусы транзакций
        tx_statuses = ['pending', 'succeeded', 'failed', 'refunded']
        for status_name in tx_statuses:
            TransactionStatus.objects.get_or_create(name=status_name)
            self.stdout.write(f'Created transaction status: {status_name}')

        # Создаем способы доставки
        DeliveryMethod.objects.get_or_create(name='courier', defaults={'price': 300})
        DeliveryMethod.objects.get_or_create(name='pickup', defaults={'price': 0})
        self.stdout.write('Created delivery methods')

        # Создаем половые группы
        genders = ['men', 'women', 'unisex', 'kids']
        for gender_name in genders:
            Gender.objects.get_or_create(name=gender_name)
            self.stdout.write(f'Created gender: {gender_name}')

        # Создаем размеры
        sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        for i, size_name in enumerate(sizes):
            Size.objects.get_or_create(name=size_name, defaults={'order': i})
            self.stdout.write(f'Created size: {size_name}')

        # Создаем цвета
        colors = [
            {'name': 'Красный', 'hex': '#FF0000'},
            {'name': 'Синий', 'hex': '#0000FF'},
            {'name': 'Зеленый', 'hex': '#00FF00'},
            {'name': 'Черный', 'hex': '#000000'},
            {'name': 'Белый', 'hex': '#FFFFFF'},
            {'name': 'Серый', 'hex': '#808080'},
            {'name': 'Бежевый', 'hex': '#F5F5DC'},
        ]
        for color in colors:
            Color.objects.get_or_create(name=color['name'], defaults={'hex_code': color['hex']})
            self.stdout.write(f'Created color: {color["name"]}')

        # Создаем категории
        categories = [
            {'name': 'Верхняя одежда', 'slug': 'outerwear'},
            {'name': 'Платья', 'slug': 'dresses'},
            {'name': 'Рубашки', 'slug': 'shirts'},
            {'name': 'Брюки', 'slug': 'pants'},
            {'name': 'Юбки', 'slug': 'skirts'},
            {'name': 'Джинсы', 'slug': 'jeans'},
            {'name': 'Футболки', 'slug': 't-shirts'},
            {'name': 'Свитеры', 'slug': 'sweaters'},
            {'name': 'Аксессуары', 'slug': 'accessories'},
        ]
        for cat in categories:
            Category.objects.get_or_create(name=cat['name'], defaults={'slug': cat['slug']})
            self.stdout.write(f'Created category: {cat["name"]}')

        # Создаем суперпользователя
        if not User.objects.filter(email='admin@clothstore.ru').exists():
            admin_role = Role.objects.get(name='admin')
            User.objects.create_superuser(
                email='admin@clothstore.ru',
                password='admin123',
                first_name='Admin',
                last_name='Admin'
            )
            self.stdout.write('Created superuser: admin@clothstore.ru')

        self.stdout.write(self.style.SUCCESS('Database initialization completed!'))