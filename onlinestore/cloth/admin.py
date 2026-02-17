from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Role, User, EmailVerification,
    Gender, Category, Size, Color,
    Product, ProductVariant, ProductImage,
    Wishlist, Cart, CartItem,
    OrderStatus, DeliveryMethod, Order, OrderItem,
    TransactionStatus, Transaction,
    Review,
)


# =========================================================
# USER & ROLE
# =========================================================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)


class EmailVerificationInline(admin.TabularInline):
    model = EmailVerification
    extra = 0
    readonly_fields = ('token', 'created_at', 'expires_at', 'is_used')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'role')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личные данные', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Роль и права', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('date_joined', 'updated_at')}),
    )
    readonly_fields = ('date_joined', 'updated_at')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active', 'is_staff'),
        }),
    )

    inlines = [EmailVerificationInline]


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used',)
    search_fields = ('user__email',)


# =========================================================
# CATALOG
# =========================================================

@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'order')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code')
    search_fields = ('name',)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size', 'color', 'price', 'stock_quantity', 'sku')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_main', 'order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active', 'is_new', 'is_bestseller', 'created_at')
    list_filter = ('is_active', 'is_new', 'is_bestseller', 'category', 'gender')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'is_new', 'is_bestseller')
    date_hierarchy = 'created_at'
    inlines = [ProductVariantInline, ProductImageInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'price', 'stock_quantity', 'sku', 'in_stock')
    list_filter = ('size', 'color')
    search_fields = ('product__name', 'sku')

    def in_stock(self, obj):
        return obj.in_stock
    in_stock.boolean = True
    in_stock.short_description = 'В наличии'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_main', 'order')
    list_filter = ('is_main',)


# =========================================================
# WISHLIST
# =========================================================

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__email', 'product__name')


# =========================================================
# CART
# =========================================================

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('get_total_price',)

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Сумма'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total_items', 'get_total_price', 'updated_at')
    search_fields = ('user__email',)
    inlines = [CartItemInline]

    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Товаров'

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Сумма'


# =========================================================
# ORDERS
# =========================================================

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('variant', 'quantity', 'price_per_unit', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__email', 'delivery_address')
    date_hierarchy = 'created_at'
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]


# =========================================================
# PAYMENTS
# =========================================================

@admin.register(TransactionStatus)
class TransactionStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'order', 'amount', 'payment_system', 'status', 'created_at')
    list_filter = ('status', 'payment_system', 'created_at')
    search_fields = ('external_id', 'order__order_number')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


# =========================================================
# REVIEWS
# =========================================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_moderated', 'moderated_by', 'created_at')
    list_filter = ('is_moderated', 'rating', 'created_at')
    search_fields = ('product__name', 'user__email', 'comment')
    date_hierarchy = 'created_at'
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_moderated=True, moderated_by=request.user)
        self.message_user(request, f'{updated} отзывов одобрено.')
    approve_reviews.short_description = 'Одобрить выбранные отзывы'
