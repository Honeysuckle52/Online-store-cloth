import uuid
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import EmailVerification
import logging

logger = logging.getLogger(__name__)


def send_verification_email(user, request):
    """
    Отправка письма для подтверждения email
    """
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

        # Отправляем письмо
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Verification email sent to {user.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
        return False


def send_password_reset_email(user, request):
    """
    Отправка письма для сброса пароля
    """
    try:
        # Создаем токен для сброса пароля
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(hours=1)

        # Сохраняем в базу (можно создать отдельную модель)
        # Для простоты используем ту же модель EmailVerification
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

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Password reset email sent to {user.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {e}")
        return False