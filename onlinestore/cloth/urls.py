from django.urls import path
from . import views

urlpatterns = [
    # Главная и каталог
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),

    # Избранное
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    # Корзина
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    # Заказы
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    # Платежи
    path('payment/<int:order_id>/', views.payment_process, name='payment'),
    path('payment/result/<int:order_id>/', views.payment_result, name='payment_result'),
    path('payment/webhook/yookassa/', views.yookassa_webhook, name='yookassa_webhook'),

    # Аутентификация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),

    # Модерация отзывов
    path('moderate/reviews/', views.moderate_reviews, name='moderate_reviews'),
    path('moderate/review/<int:review_id>/approve/', views.approve_review, name='approve_review'),
    path('moderate/review/<int:review_id>/reject/', views.reject_review, name='reject_review'),

    # Управление товарами
    path('manage/products/', views.manage_products, name='manage_products'),
    path('manage/product/add/', views.edit_product, name='add_product'),
    path('manage/product/<int:product_id>/edit/', views.edit_product, name='edit_product'),

    # Управление заказами
    path('manage/orders/', views.manage_orders, name='manage_orders'),
    path('manage/order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),

    # Админ панель (изменено с /admin/dashboard/ на /dashboard/)
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('export/orders/', views.export_orders, name='export_orders'),

    # Верификация email
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),

    # Сброс пароля
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uuid:token>/', views.reset_password, name='reset_password'),
]
