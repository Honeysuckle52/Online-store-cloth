import uuid
from datetime import timedelta
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string
from .models import EmailVerification
import logging
import socket
import smtplib

logger = logging.getLogger(__name__)


def send_verification_email(user, request):
    """
    Отправка письма для подтверждения email
    """
    verification_url = None

    try:
        # Создаем токен верификации
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(hours=24)

        # Сохраняем в базу
        verification = EmailVerification.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

        # Формируем ссылку для подтверждения
        verification_url = request.build_absolute_uri(
            reverse('verify_email', args=[token])
        )

        # Тема письма
        subject = 'Подтверждение email - Интернет-магазин CLOTH'

        # Текст письма
        message = f"""
Здравствуйте, {user.get_full_name() or user.email}!

Благодарим вас за регистрацию в интернет-магазине CLOTH.

Для подтверждения вашего email перейдите по ссылке:
{verification_url}

Ссылка действительна в течение 24 часов.

Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.

С уважением,
Команда CLOTH
        """

        # HTML версия письма
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #4A3F35;
            background-color: #FAF9F6;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: white;
            border-radius: 24px;
            padding: 40px;
            border: 1px solid #E9DBCB;
            box-shadow: 0 10px 30px rgba(74, 63, 53, 0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo {{
            font-family: 'Playfair Display', serif;
            font-size: 2rem;
            font-weight: 700;
            color: #4A3F35;
            text-decoration: none;
        }}
        .button {{
            display: inline-block;
            padding: 15px 40px;
            background: #D4A373;
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            margin: 30px 0;
            transition: all 0.3s ease;
        }}
        .button:hover {{
            background: #B88B5E;
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(212, 163, 115, 0.3);
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #E9DBCB;
            text-align: center;
            color: #8C7E72;
            font-size: 0.9rem;
        }}
        .note {{
            background: #FAF9F6;
            padding: 15px;
            border-radius: 12px;
            color: #8C7E72;
            font-size: 0.9rem;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">CLOTH.</div>
        </div>

        <h2 style="text-align: center; color: #4A3F35;">Подтверждение email</h2>

        <p>Здравствуйте, <strong>{user.get_full_name() or user.email}</strong>!</p>

        <p>Благодарим вас за регистрацию в интернет-магазине <strong>CLOTH</strong>.</p>

        <p>Для подтверждения вашего email и активации аккаунта нажмите на кнопку ниже:</p>

        <div style="text-align: center;">
            <a href="{verification_url}" class="button">Подтвердить email</a>
        </div>

        <p>Или скопируйте ссылку в браузер:</p>
        <div style="background: #FAF9F6; padding: 10px; border-radius: 8px; word-break: break-all;">
            {verification_url}
        </div>

        <div class="note">
            <p>⚠️ Ссылка действительна в течение <strong>24 часов</strong>.</p>
            <p>📧 Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.</p>
        </div>

        <div class="footer">
            <p>С уважением, команда CLOTH</p>
            <p style="margin-top: 10px;">
                <a href="https://cloth-store.ru" style="color: #D4A373; text-decoration: none;">cloth-store.ru</a>
            </p>
        </div>
    </div>
</body>
</html>
        """

        # В режиме разработки выводим в консоль
        if settings.DEBUG:
            print(f"\n{'=' * 60}")
            print(f"📧 ПИСЬМО ДЛЯ ПОДТВЕРЖДЕНИЯ")
            print(f"{'=' * 60}")
            print(f"Кому: {user.email}")
            print(f"Ссылка: {verification_url}")
            print(f"{'=' * 60}\n")

        # Пытаемся отправить реальное письмо
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # Используем EMAIL_HOST_USER вместо DEFAULT_FROM_EMAIL
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Verification email sent to {user.email}")
            if settings.DEBUG:
                print(f"✅ Письмо успешно отправлено на {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            if settings.DEBUG:
                print(f"❌ Ошибка отправки: {e}")
                print(f"ℹ️ Используйте ссылку выше для подтверждения")
            return False

    except Exception as e:
        logger.error(f"Failed to create verification for {user.email}: {e}")
        if settings.DEBUG and verification_url:
            print(f"\n{'=' * 60}")
            print(f"📧 ПИСЬМО ДЛЯ ПОДТВЕРЖДЕНИЯ")
            print(f"{'=' * 60}")
            print(f"Кому: {user.email}")
            print(f"Ссылка: {verification_url}")
            print(f"{'=' * 60}\n")
        return False


def send_password_reset_email(user, request):
    """
    Отправка письма для сброса пароля
    """
    reset_url = None

    try:
        # Создаем токен для сброса пароля
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(hours=1)

        # Сохраняем в базу
        verification = EmailVerification.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

        # Формируем ссылку для сброса пароля
        reset_url = request.build_absolute_uri(
            reverse('reset_password', args=[token])
        )

        subject = 'Сброс пароля - Интернет-магазин CLOTH'

        message = f"""
Здравствуйте, {user.get_full_name() or user.email}!

Вы запросили сброс пароля на сайте CLOTH.

Для сброса пароля перейдите по ссылке:
{reset_url}

Ссылка действительна в течение 1 часа.

Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.

С уважением,
Команда CLOTH
        """

        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #4A3F35;
            background-color: #FAF9F6;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: white;
            border-radius: 24px;
            padding: 40px;
            border: 1px solid #E9DBCB;
            box-shadow: 0 10px 30px rgba(74, 63, 53, 0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo {{
            font-family: 'Playfair Display', serif;
            font-size: 2rem;
            font-weight: 700;
            color: #4A3F35;
            text-decoration: none;
        }}
        .button {{
            display: inline-block;
            padding: 15px 40px;
            background: #D4A373;
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            margin: 30px 0;
            transition: all 0.3s ease;
        }}
        .button:hover {{
            background: #B88B5E;
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(212, 163, 115, 0.3);
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #E9DBCB;
            text-align: center;
            color: #8C7E72;
            font-size: 0.9rem;
        }}
        .warning {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 12px;
            color: #856404;
            font-size: 0.9rem;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">CLOTH.</div>
        </div>

        <h2 style="text-align: center; color: #4A3F35;">Сброс пароля</h2>

        <p>Здравствуйте, <strong>{user.get_full_name() or user.email}</strong>!</p>

        <p>Вы запросили сброс пароля на сайте <strong>CLOTH</strong>.</p>

        <p>Для создания нового пароля нажмите на кнопку ниже:</p>

        <div style="text-align: center;">
            <a href="{reset_url}" class="button">Сбросить пароль</a>
        </div>

        <div class="warning">
            <p>⚠️ Ссылка действительна в течение <strong>1 часа</strong>.</p>
            <p>🔒 Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.</p>
        </div>

        <div class="footer">
            <p>С уважением, команда CLOTH</p>
            <p style="margin-top: 10px;">
                <a href="https://cloth-store.ru" style="color: #D4A373; text-decoration: none;">cloth-store.ru</a>
            </p>
        </div>
    </div>
</body>
</html>
        """

        # В режиме разработки выводим в консоль
        if settings.DEBUG:
            print(f"\n{'=' * 60}")
            print(f"🔑 СБРОС ПАРОЛЯ")
            print(f"{'=' * 60}")
            print(f"Кому: {user.email}")
            print(f"Ссылка: {reset_url}")
            print(f"{'=' * 60}\n")

        # Пытаемся отправить реальное письмо
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Password reset email sent to {user.email}")
            if settings.DEBUG:
                print(f"✅ Письмо успешно отправлено на {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            if settings.DEBUG:
                print(f"❌ Ошибка отправки: {e}")
                print(f"ℹ️ Используйте ссылку выше для сброса пароля")
            return False

    except Exception as e:
        logger.error(f"Failed to create password reset for {user.email}: {e}")
        if settings.DEBUG and reset_url:
            print(f"\n{'=' * 60}")
            print(f"🔑 СБРОС ПАРОЛЯ")
            print(f"{'=' * 60}")
            print(f"Кому: {user.email}")
            print(f"Ссылка: {reset_url}")
            print(f"{'=' * 60}\n")
        return False


def send_order_confirmation_email(order, request):
    """
    Отправка письма о подтверждении заказа
    """
    try:
        user = order.user
        payment_method_display = dict(order.PAYMENT_METHOD_CHOICES).get(order.payment_method, order.payment_method)

        # Формируем строку с товарами
        items_html = ""
        items_text = ""
        for item in order.items.all():
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #E9DBCB;">
                    {item.variant.product.name}
                    {f" ({item.variant.size.name})" if item.variant.size else ""}
                    {f" - {item.variant.color.name}" if item.variant.color else ""}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #E9DBCB; text-align: center;">
                    {item.quantity}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #E9DBCB; text-align: right;">
                    {item.price_per_unit} ₽
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #E9DBCB; text-align: right; font-weight: 600;">
                    {item.total_price()} ₽
                </td>
            </tr>
            """
            items_text += f"  - {item.variant.product.name} x{item.quantity} = {item.total_price()} ₽\n"

        subject = f'Заказ #{order.order_number} оформлен - CLOTH'

        message = f"""
Здравствуйте, {user.get_full_name() or user.email}!

Ваш заказ #{order.order_number} успешно оформлен.

Сумма заказа: {order.total_amount} ₽
Способ оплаты: {payment_method_display}
Адрес доставки: {order.delivery_address}

Состав заказа:
{items_text}
Мы свяжемся с вами в ближайшее время для подтверждения заказа.

С уважением,
Команда CLOTH
        """

        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #4A3F35;
            background-color: #FAF9F6;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: white;
            border-radius: 24px;
            padding: 40px;
            border: 1px solid #E9DBCB;
            box-shadow: 0 10px 30px rgba(74, 63, 53, 0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo {{
            font-family: 'Playfair Display', serif;
            font-size: 2rem;
            font-weight: 700;
            color: #4A3F35;
        }}
        .order-number {{
            font-size: 1.5rem;
            color: #D4A373;
            font-weight: 600;
            text-align: center;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
        }}
        th {{
            background: #F2EDE4;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }}
        .total-row {{
            background: #F2EDE4;
            font-weight: 700;
        }}
        .info-box {{
            background: #FAF9F6;
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #E9DBCB;
            text-align: center;
            color: #8C7E72;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">CLOTH.</div>
        </div>

        <h2 style="text-align: center; color: #4A3F35;">Заказ успешно оформлен!</h2>

        <div class="order-number">№ {order.order_number}</div>

        <p>Здравствуйте, <strong>{user.get_full_name() or user.email}</strong>!</p>

        <p>Спасибо за ваш заказ в интернет-магазине <strong>CLOTH</strong>.</p>

        <div class="info-box">
            <p><strong>Способ оплаты:</strong> {payment_method_display}</p>
            <p><strong>Адрес доставки:</strong> {order.delivery_address}</p>
            {f'<p><strong>Комментарий:</strong> {order.comment}</p>' if order.comment else ''}
        </div>

        <h3>Состав заказа:</h3>

        <table>
            <thead>
                <tr>
                    <th>Товар</th>
                    <th>Кол-во</th>
                    <th>Цена</th>
                    <th>Сумма</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
                <tr class="total-row">
                    <td colspan="3" style="padding: 15px; text-align: right;">Итого:</td>
                    <td style="padding: 15px; text-align: right; color: #D4A373;">{order.total_amount} ₽</td>
                </tr>
            </tbody>
        </table>

        <p>Мы свяжемся с вами в ближайшее время для уточнения деталей доставки.</p>

        <div class="footer">
            <p>С уважением, команда CLOTH</p>
            <p><a href="https://cloth-store.ru" style="color: #D4A373; text-decoration: none;">cloth-store.ru</a></p>
        </div>
    </div>
</body>
</html>
        """

        if settings.DEBUG:
            print(f"\n{'=' * 60}")
            print(f"📦 ПОДТВЕРЖДЕНИЕ ЗАКАЗА #{order.order_number}")
            print(f"{'=' * 60}")
            print(f"Кому: {user.email}")
            print(f"Сумма: {order.total_amount} ₽")
            print(f"{'=' * 60}\n")

        # Пытаемся отправить реальное письмо
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Order confirmation email sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send order confirmation email: {e}")
            if settings.DEBUG:
                print(f"❌ Ошибка отправки: {e}")
            return False

    except Exception as e:
        logger.error(f"Failed to create order confirmation for {order.order_number}: {e}")
        return False