from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, Avg
import uuid


# =========================================================
# USER & ROLE
# =========================================================

class Role(models.Model):
    """Роли пользователей"""
    ROLE_CHOICES = (
        ("user", "Пользователь"),
        ("moderator", "Модератор"),
        ("admin", "Администратор"),
    )
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")

        email = self.normalize_email(email)

        # Получаем или создаем роль по умолчанию
        role, created = Role.objects.get_or_create(name="user")
        extra_fields.setdefault('role', role)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        role, created = Role.objects.get_or_create(name="admin")
        extra_fields.setdefault('role', role)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя"""
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Фамилия")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")

    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='users', verbose_name="Роль")

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")

    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        indexes = [
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name


class EmailVerification(models.Model):
    """Верификация email"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Верификация email"
        verbose_name_plural = "Верификации email"
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.token}"

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at


# =========================================================
# CATALOG
# =========================================================

class Gender(models.Model):
    """Пол/возрастная группа"""
    GENDER_CHOICES = (
        ("men", "Мужской"),
        ("women", "Женский"),
        ("unisex", "Унисекс"),
        ("kids", "Детский"),
    )
    name = models.CharField(max_length=20, choices=GENDER_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = "Пол/группа"
        verbose_name_plural = "Пол/группы"


class Category(models.Model):
    """Категория товаров"""
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Изображение")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Size(models.Model):
    """Размер"""
    name = models.CharField(max_length=20, unique=True, verbose_name="Размер")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"
        ordering = ['order']

    def __str__(self):
        return self.name


class Color(models.Model):
    """Цвет"""
    name = models.CharField(max_length=50, verbose_name="Название")
    hex_code = models.CharField(max_length=7, verbose_name="HEX код", help_text="Например: #FF5733")

    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар"""
    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")

    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Цена")

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products',
                                 verbose_name="Категория")
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пол/группа")

    material = models.CharField(max_length=255, blank=True, verbose_name="Материал")
    care_instructions = models.TextField(blank=True, verbose_name="Уход")

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_new = models.BooleanField(default=False, verbose_name="Новинка")
    is_bestseller = models.BooleanField(default=False, verbose_name="Хит продаж")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["price"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_average_rating(self):
        """Получить средний рейтинг"""
        result = self.reviews.filter(is_moderated=True).aggregate(Avg('rating'))
        return result['rating__avg'] or 0

    def get_main_image(self):
        """Получить главное изображение"""
        return self.images.filter(is_main=True).first() or self.images.first()


class ProductVariant(models.Model):
    """Вариант товара (размер/цвет)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name="Товар")
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Размер")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Цвет")

    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Цена")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")

    sku = models.CharField(max_length=100, unique=True, blank=True, verbose_name="Артикул")

    class Meta:
        verbose_name = "Вариант товара"
        verbose_name_plural = "Варианты товаров"
        unique_together = ('product', 'size', 'color')

    def __str__(self):
        attrs = []
        if self.size:
            attrs.append(str(self.size))
        if self.color:
            attrs.append(str(self.color))
        attrs_str = f" ({', '.join(attrs)})" if attrs else ""
        return f"{self.product.name}{attrs_str}"

    @property
    def in_stock(self):
        """Проверка наличия на складе"""
        return self.stock_quantity > 0

    def save(self, *args, **kwargs):
        if not self.sku:
            base = f"{self.product.id}"
            if self.size:
                base += f"-{self.size.id}"
            if self.color:
                base += f"-{self.color.id}"
            self.sku = base
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Изображение товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Товар")
    image = models.ImageField(upload_to='products/%Y/%m/', verbose_name="Изображение")
    is_main = models.BooleanField(default=False, verbose_name="Главное")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ['-is_main', 'order']

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


# =========================================================
# WISHLIST
# =========================================================

class Wishlist(models.Model):
    """Избранное"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist', verbose_name="Пользователь")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by', verbose_name="Товар")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"


# =========================================================
# CART
# =========================================================

class Cart(models.Model):
    """Корзина"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Cart of {self.user.email}"

    def get_total_price(self):
        """Общая стоимость"""
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        """Общее количество товаров"""
        return self.items.aggregate(models.Sum('quantity'))['quantity__sum'] or 0


class CartItem(models.Model):
    """Элемент корзины"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Корзина")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='cart_items',
                                verbose_name="Вариант товара")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
        unique_together = ('cart', 'variant')

    def __str__(self):
        return f"{self.variant.product.name} x{self.quantity}"

    def get_total_price(self):
        """Стоимость позиции"""
        return self.variant.price * self.quantity


# =========================================================
# ORDERS
# =========================================================

class OrderStatus(models.Model):
    """Статус заказа"""
    STATUS_CHOICES = (
        ('created', 'Создан'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    )
    name = models.CharField(max_length=20, choices=STATUS_CHOICES, unique=True, verbose_name="Статус")

    class Meta:
        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказов"

    def __str__(self):
        return self.get_name_display()


class DeliveryMethod(models.Model):
    """Способ доставки"""
    METHOD_CHOICES = (
        ('courier', 'Курьер'),
        ('pickup', 'Самовывоз'),
    )
    name = models.CharField(max_length=20, choices=METHOD_CHOICES, unique=True, verbose_name="Способ доставки")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Стоимость")

    class Meta:
        verbose_name = "Способ доставки"
        verbose_name_plural = "Способы доставки"

    def __str__(self):
        return self.get_name_display()


class Order(models.Model):
    """Заказ"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Пользователь")

    order_number = models.CharField(max_length=50, unique=True, verbose_name="Номер заказа")

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")
    delivery_address = models.TextField(verbose_name="Адрес доставки")

    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.SET_NULL, null=True, blank=True,
                                        verbose_name="Способ доставки")
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, related_name='orders', verbose_name="Статус")

    comment = models.TextField(blank=True, verbose_name="Комментарий")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            date_part = timezone.now().strftime('%Y%m%d')
            last_today = Order.objects.filter(order_number__startswith=date_part).count()
            self.order_number = f"{date_part}{last_today + 1:04d}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Позиция заказа"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, verbose_name="Вариант товара")

    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"

    def __str__(self):
        return f"{self.variant.product.name} x{self.quantity}"

    def total_price(self):
        """Общая стоимость позиции"""
        return self.price_per_unit * self.quantity


# =========================================================
# PAYMENTS
# =========================================================

class TransactionStatus(models.Model):
    """Статус транзакции"""
    STATUS_CHOICES = (
        ('pending', 'Ожидание'),
        ('succeeded', 'Успешно'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возврат'),
    )
    name = models.CharField(max_length=20, choices=STATUS_CHOICES, unique=True, verbose_name="Статус")

    class Meta:
        verbose_name = "Статус транзакции"
        verbose_name_plural = "Статусы транзакций"

    def __str__(self):
        return self.get_name_display()


class Transaction(models.Model):
    """Транзакция"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions', verbose_name="Заказ")

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    payment_system = models.CharField(max_length=50, default='YooKassa', verbose_name="Платёжная система")

    external_id = models.CharField(max_length=255, unique=True, verbose_name="Внешний ID")

    status = models.ForeignKey(TransactionStatus, on_delete=models.PROTECT, related_name='transactions',
                               verbose_name="Статус")

    payment_data = models.JSONField(default=dict, blank=True, verbose_name="Данные платежа")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        indexes = [
            models.Index(fields=['external_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Транзакция {self.external_id} - {self.amount} ₽"


# =========================================================
# REVIEWS
# =========================================================

class Review(models.Model):
    """Отзыв"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Товар")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name="Пользователь")

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка"
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    is_moderated = models.BooleanField(default=False, verbose_name="Промодерировано")
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='moderated_reviews', verbose_name="Модератор")
    moderated_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата модерации")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        unique_together = ('product', 'user')
        indexes = [
            models.Index(fields=["rating"]),
            models.Index(fields=["is_moderated"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.rating}/5"