from django.core.management.base import BaseCommand
from ...models import Product
import re


TRANSLIT_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def cyrillic_slugify(text):
    text = text.lower().strip()
    result = []
    for char in text:
        if char in TRANSLIT_MAP:
            result.append(TRANSLIT_MAP[char])
        elif char == ' ' or char == '-':
            result.append('-')
        elif char.isascii() and char.isalnum():
            result.append(char)
        else:
            result.append('')
    slug = ''.join(result)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug


class Command(BaseCommand):
    help = 'Исправляет битые slug у товаров (пробелы, кириллица)'

    def handle(self, *args, **options):
        products = Product.objects.all()
        fixed = 0

        for product in products:
            old_slug = product.slug
            # Проверяем: есть пробелы, кириллица, или slug пустой
            needs_fix = (
                not old_slug
                or ' ' in old_slug
                or any(c in TRANSLIT_MAP for c in old_slug.lower())
            )

            if needs_fix:
                base_slug = cyrillic_slugify(product.name)
                slug = base_slug
                counter = 1
                while Product.objects.filter(slug=slug).exclude(pk=product.pk).exists():
                    slug = f'{base_slug}-{counter}'
                    counter += 1

                product.slug = slug
                product.save(update_fields=['slug'])
                fixed += 1
                self.stdout.write(f'  "{old_slug}" -> "{slug}" ({product.name})')

        if fixed:
            self.stdout.write(self.style.SUCCESS(f'\nИсправлено {fixed} slug(ов)'))
        else:
            self.stdout.write(self.style.SUCCESS('Все slug корректны, исправлений не требуется'))
