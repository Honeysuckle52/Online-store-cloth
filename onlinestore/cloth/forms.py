from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User, Order, Review, ProductVariant, Role
import re


class RegisterForm(forms.ModelForm):
    """Форма регистрации"""
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
                'autocomplete': 'email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя',
                'autocomplete': 'given-name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия',
                'autocomplete': 'family-name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Телефон (необязательно)',
                'autocomplete': 'tel'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Удаляем все нецифровые символы
            phone_clean = re.sub(r'\D', '', phone)
            if len(phone_clean) < 10 or len(phone_clean) > 15:
                raise ValidationError('Введите корректный номер телефона')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают')

        if password1 and len(password1) < 8:
            raise ValidationError('Пароль должен содержать минимум 8 символов')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False  # Делаем пользователя неактивным до подтверждения email

        # Назначаем роль по умолчанию
        try:
            # Пытаемся получить существующую роль
            default_role = Role.objects.get(name='user')
        except Role.DoesNotExist:
            # Если роль не существует, создаем ее
            default_role = Role.objects.create(name='user')

        user.role = default_role

        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Форма входа"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль',
            'autocomplete': 'current-password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise ValidationError('Неверный email или пароль')
            if not user.is_active:
                raise ValidationError('Аккаунт деактивирован. Пожалуйста, подтвердите email.')

            self.user = user

        return cleaned_data


class CheckoutForm(forms.ModelForm):
    """Форма оформления заказа"""
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Комментарий к заказу (необязательно)'
        })
    )

    class Meta:
        model = Order
        fields = ['delivery_address']
        widgets = {
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите адрес доставки'
            }),
        }

    def clean_delivery_address(self):
        address = self.cleaned_data.get('delivery_address')
        if not address or len(address.strip()) < 10:
            raise ValidationError('Введите полный адрес доставки')
        return address.strip()


class ReviewForm(forms.ModelForm):
    """Форма отзыва"""

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'rating-radio'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Поделитесь своим мнением о товаре...'
            }),
        }
        labels = {
            'rating': 'Оценка',
            'comment': 'Комментарий',
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating not in [1, 2, 3, 4, 5]:
            raise ValidationError('Оценка должна быть от 1 до 5')
        return rating


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Телефон'
            }),
        }


class ProductFilterForm(forms.Form):
    """Форма фильтрации товаров"""
    SORT_CHOICES = [
        ('-created_at', 'Новинки'),
        ('price', 'Сначала дешевле'),
        ('-price', 'Сначала дороже'),
        ('name', 'По названию (А-Я)'),
        ('-name', 'По названию (Я-А)'),
    ]

    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'От',
            'min': 0,
            'step': 100
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'До',
            'min': 0,
            'step': 100
        })
    )
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    in_stock = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')

        if min_price and max_price and min_price > max_price:
            raise ValidationError('Минимальная цена не может быть больше максимальной')

        return cleaned_data


class AddToCartForm(forms.Form):
    """Форма добавления в корзину"""
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'value': 1
        })
    )
    variant_id = forms.IntegerField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()
        variant_id = cleaned_data.get('variant_id')
        quantity = cleaned_data.get('quantity')

        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id)
                if quantity > variant.stock_quantity:
                    raise ValidationError(f'Доступно только {variant.stock_quantity} шт.')
            except ProductVariant.DoesNotExist:
                raise ValidationError('Товар не найден')

        return cleaned_data