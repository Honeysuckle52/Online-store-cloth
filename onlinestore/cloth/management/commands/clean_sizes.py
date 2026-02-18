from django.core.management.base import BaseCommand
from cloth.models import Size


class Command(BaseCommand):
    help = 'Remove numeric sizes and keep only letter sizes'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning sizes...')

        # Удаляем числовые размеры
        numeric_sizes = Size.objects.filter(name__regex=r'^\d+$')
        count = numeric_sizes.count()
        numeric_sizes.delete()
        self.stdout.write(f'Removed {count} numeric sizes')

        # Создаем буквенные размеры, если их нет
        letter_sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
        for i, size_name in enumerate(letter_sizes):
            size, created = Size.objects.get_or_create(
                name=size_name,
                defaults={'order': i}
            )
            if created:
                self.stdout.write(f'Created size: {size_name}')

        self.stdout.write(self.style.SUCCESS('Sizes cleaned successfully!'))