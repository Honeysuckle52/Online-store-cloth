from django.core.management.base import BaseCommand
from django.conf import settings
from ...models import Product, ProductImage
from pathlib import Path


class Command(BaseCommand):
    help = 'Привязывает фотографии к товарам'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n' + '=' * 60))
        self.stdout.write(self.style.WARNING('ПРИВЯЗКА ФОТОГРАФИЙ К ТОВАРАМ'))
        self.stdout.write(self.style.WARNING('=' * 60 + '\n'))

        media_path = settings.MEDIA_ROOT / 'products'

        if not media_path.exists():
            self.stdout.write(self.style.ERROR(f'Папка {media_path} не найдена!'))
            return

        # Показываем файлы в папке
        self.stdout.write('\n📁 Файлы в папке:')
        files = []
        for file in media_path.glob('*.png'):
            files.append(file.name)
            self.stdout.write(f'  - {file.name}')

        if not files:
            self.stdout.write(self.style.ERROR('  Папка пуста!'))
            return

        # Удаляем старые записи из БД
        self.stdout.write('\n🗑️ Удаление старых записей...')
        old_count = ProductImage.objects.count()
        ProductImage.objects.all().delete()
        self.stdout.write(f'  Удалено записей: {old_count}')

        # Точное сопоставление файлов с товарами
        product_mapping = {
            'bazafutbolka.png': 'Базовая футболка',
            'oversaiz.png': 'Оверсайз футболка',
            'letneeplatie.png': 'Летнее платье',
            'rubaskaplatie.png': 'Платье-рубашка',
            'djinskurtka.png': 'Джинсовая куртка',
            'vetrovka.png': 'Легкая ветровка',
            'sviterblack.png': 'Вязаный свитер',
            'beliedjemper.png': 'Тонкий джемпер',
            'rubashkakrasnai.png': 'Классическая рубашка',
            'rubashkalen.png': 'Льняная рубашка',
            'bruki.png': 'Классические брюки',
            'chinos.png': 'Чиносы',
            'ybkakarandash.png': 'Юбка-карандаш',
            'ybkaplise.png': 'Юбка плиссе',
            'djinskras.png': 'Классические джинсы',
            'djinssvisokoi.png': 'Джинсы с высокой талией',
            'bezshapka1.png': 'Шапка',
            'bezshapka2.png': 'Шарф',
        }

        # Привязываем файлы к товарам
        self.stdout.write('\n🔗 Привязка к товарам...')

        assigned = 0
        not_found = []

        for filename, product_name in product_mapping.items():
            if filename not in files:
                self.stdout.write(self.style.WARNING(f'  ? {filename} - файл отсутствует'))
                continue

            # Ищем товар по точному названию
            product = Product.objects.filter(name__icontains=product_name).first()

            if product:
                ProductImage.objects.create(
                    product=product,
                    image=f'products/{filename}',
                    is_main=True
                )
                self.stdout.write(self.style.SUCCESS(f'  ✓ {filename} -> "{product.name}"'))
                assigned += 1
            else:
                not_found.append(f'{filename} (искали: {product_name})')
                self.stdout.write(self.style.WARNING(f'  ? {filename} - товар "{product_name}" не найден'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'✅ Привязано изображений: {assigned}'))

        if not_found:
            self.stdout.write(self.style.WARNING('\n⚠ Товары не найдены для:'))
            for item in not_found:
                self.stdout.write(f'  {item}')

        self.stdout.write(self.style.SUCCESS('=' * 60 + '\n'))