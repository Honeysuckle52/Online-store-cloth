import uuid
import logging
from decimal import Decimal

from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail

import yookassa
from yookassa import Payment, Configuration
from yookassa.domain.notification import WebhookNotification

from .models import Transaction, TransactionStatus, Order, OrderStatus

logger = logging.getLogger(__name__)


class YooKassaClient:
    """Клиент для работы с API ЮKassa"""

    def __init__(self):
        """Инициализация клиента с настройками из settings.py"""
        Configuration.account_id = settings.YOOKASSA_SHOP_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    def create_payment(self, order, return_url):
        """
        Создание платежа в ЮKassa

        Args:
            order: Объект заказа
            return_url: URL для возврата после оплаты

        Returns:
            Объект платежа или None в случае ошибки
        """
        try:
            # Генерируем уникальный ключ идемпотентности
            idempotence_key = str(uuid.uuid4())

            # Создаем платеж
            payment = Payment.create({
                "amount": {
                    "value": f"{order.total_amount:.2f}",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url
                },
                "capture": True,  # Автоматическое подтверждение платежа
                "description": f"Оплата заказа №{order.order_number} в магазине CLOTH",
                "metadata": {
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "user_id": order.user.id,
                    "user_email": order.user.email
                },
                "receipt": {
                    "customer": {
                        "email": order.user.email
                    },
                    "items": self._get_receipt_items(order)
                }
            }, idempotence_key)

            logger.info(f"Payment created: {payment.id} for order {order.order_number}")
            return payment

        except Exception as e:
            logger.error(f"Failed to create payment for order {order.order_number}: {e}")
            return None

    def get_payment_info(self, payment_id):
        """
        Получение информации о платеже

        Args:
            payment_id: ID платежа в ЮKassa

        Returns:
            Объект платежа или None в случае ошибки
        """
        try:
            payment = Payment.find_one(payment_id)
            return payment
        except Exception as e:
            logger.error(f"Failed to get payment info for {payment_id}: {e}")
            return None

    def capture_payment(self, payment_id, amount=None):
        """
        Подтверждение платежа (если не использован auto-capture)

        Args:
            payment_id: ID платежа в ЮKassa
            amount: Сумма для подтверждения (если нужно подтвердить частичную сумму)

        Returns:
            Объект платежа или None в случае ошибки
        """
        try:
            idempotence_key = str(uuid.uuid4())

            capture_data = {}
            if amount:
                capture_data["amount"] = {
                    "value": f"{amount:.2f}",
                    "currency": "RUB"
                }

            payment = Payment.capture(payment_id, capture_data, idempotence_key)
            logger.info(f"Payment captured: {payment_id}")
            return payment

        except Exception as e:
            logger.error(f"Failed to capture payment {payment_id}: {e}")
            return None

    def cancel_payment(self, payment_id):
        """
        Отмена платежа

        Args:
            payment_id: ID платежа в ЮKassa

        Returns:
            Объект платежа или None в случае ошибки
        """
        try:
            idempotence_key = str(uuid.uuid4())
            payment = Payment.cancel(payment_id, idempotence_key)
            logger.info(f"Payment canceled: {payment_id}")
            return payment

        except Exception as e:
            logger.error(f"Failed to cancel payment {payment_id}: {e}")
            return None

    def refund_payment(self, payment_id, amount):
        """
        Возврат платежа

        Args:
            payment_id: ID платежа в ЮKassa
            amount: Сумма возврата

        Returns:
            Объект возврата или None в случае ошибки
        """
        try:
            from yookassa import Refund

            idempotence_key = str(uuid.uuid4())

            refund = Refund.create({
                "payment_id": payment_id,
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": "RUB"
                }
            }, idempotence_key)

            logger.info(f"Refund created: {refund.id} for payment {payment_id}")
            return refund

        except Exception as e:
            logger.error(f"Failed to refund payment {payment_id}: {e}")
            return None

    def _get_receipt_items(self, order):
        """
        Формирование элементов чека для платежа

        Args:
            order: Объект заказа

        Returns:
            Список товаров для чека
        """
        items = []

        for item in order.items.all():
            items.append({
                "description": item.variant.product.name[:128],  # ЮKassa ограничивает длину
                "quantity": item.quantity,
                "amount": {
                    "value": f"{item.price_per_unit:.2f}",
                    "currency": "RUB"
                },
                "vat_code": 1,  # Без НДС (для большинства товаров)
                "payment_mode": "full_payment",
                "payment_subject": "commodity"
            })

        # Добавляем доставку как отдельный товар (если платная)
        # if order.delivery_price and order.delivery_price > 0:
        #     items.append({
        #         "description": "Доставка",
        #         "quantity": 1,
        #         "amount": {
        #             "value": f"{order.delivery_price:.2f}",
        #             "currency": "RUB"
        #         },
        #         "vat_code": 1,
        #         "payment_mode": "full_payment",
        #         "payment_subject": "service"
        #     })

        return items


class PaymentService:
    """Сервис для работы с платежами в приложении"""

    def __init__(self):
        self.yookassa = YooKassaClient()

    def process_payment(self, order, request):
        """
        Обработка платежа для заказа

        Args:
            order: Объект заказа
            request: HTTP запрос

        Returns:
            URL для перенаправления на оплату или None
        """
        # Проверяем, что заказ еще не оплачен
        if order.status.name in ['paid', 'shipped', 'delivered']:
            logger.warning(f"Order {order.order_number} already paid")
            return None

        # Создаем URL для возврата
        return_url = request.build_absolute_uri(
            reverse('payment_result', args=[order.id])
        )

        # Создаем платеж в ЮKassa
        payment = self.yookassa.create_payment(order, return_url)

        if payment:
            # Сохраняем информацию о транзакции
            status_pending, _ = TransactionStatus.objects.get_or_create(name='pending')

            Transaction.objects.create(
                order=order,
                amount=order.total_amount,
                payment_system='YooKassa',
                external_id=payment.id,
                status=status_pending,
                payment_data={
                    'payment_id': payment.id,
                    'confirmation_url': payment.confirmation.confirmation_url,
                    'created_at': str(payment.created_at)
                }
            )

            # Возвращаем URL для перенаправления
            return payment.confirmation.confirmation_url

        return None

    def handle_successful_payment(self, payment_id):
        """
        Обработка успешного платежа

        Args:
            payment_id: ID платежа в ЮKassa

        Returns:
            Объект заказа или None
        """
        # Находим транзакцию
        try:
            transaction = Transaction.objects.get(external_id=payment_id)
        except Transaction.DoesNotExist:
            logger.error(f"Transaction not found for payment {payment_id}")
            return None

        # Получаем информацию о платеже
        payment = self.yookassa.get_payment_info(payment_id)

        if payment and payment.status == 'succeeded':
            # Обновляем статус транзакции
            status_succeeded, _ = TransactionStatus.objects.get_or_create(name='succeeded')
            transaction.status = status_succeeded
            transaction.save()

            # Обновляем статус заказа
            status_paid, _ = OrderStatus.objects.get_or_create(name='paid')
            order = transaction.order
            order.status = status_paid
            order.payment_method = 'yookassa'
            order.save()

            # Списываем товары со склада
            for order_item in order.items.select_related('variant').all():
                variant = order_item.variant
                variant.stock_quantity -= order_item.quantity
                if variant.stock_quantity < 0:
                    variant.stock_quantity = 0
                variant.save()

            # Очищаем корзину пользователя
            from .models import Cart
            try:
                cart = Cart.objects.get(user=order.user)
                cart.items.all().delete()
            except Cart.DoesNotExist:
                pass

            logger.info(f"Payment {payment_id} succeeded for order {order.order_number}")

            # Отправляем уведомление
            self.send_payment_notification(order)

            return order

        return None

    def handle_failed_payment(self, payment_id):
        """
        Обработка неуспешного платежа -- склад НЕ трогаем (он не был списан),
        корзину НЕ трогаем (она не была очищена), просто помечаем заказ как отмененный.

        Args:
            payment_id: ID платежа в ЮKassa

        Returns:
            Объект транзакции или None
        """
        try:
            transaction = Transaction.objects.get(external_id=payment_id)
        except Transaction.DoesNotExist:
            logger.error(f"Transaction not found for payment {payment_id}")
            return None

        # Обновляем статус транзакции
        status_failed, _ = TransactionStatus.objects.get_or_create(name='failed')
        transaction.status = status_failed
        transaction.save()

        # Помечаем заказ как отмененный
        status_cancelled, _ = OrderStatus.objects.get_or_create(name='cancelled')
        order = transaction.order
        order.status = status_cancelled
        order.save()

        logger.info(f"Payment {payment_id} failed for order {order.order_number}, order cancelled")

        return transaction

    def send_payment_notification(self, order):
        """
        Отправка уведомления об успешной оплате

        Args:
            order: Объект заказа
        """
        subject = f'Оплата заказа #{order.order_number} подтверждена'
        message = f"""
        Здравствуйте, {order.user.get_full_name() or order.user.email}!

        Оплата вашего заказа #{order.order_number} подтверждена.

        Детали заказа:
        • Номер заказа: {order.order_number}
        • Сумма: {order.total_amount} ₽
        • Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}
        • Статус: {order.status.get_name_display()}

        Мы начинаем готовить ваш заказ к отправке.
        Вы можете отслеживать статус заказа в личном кабинете.

        Спасибо за покупку!

        С уважением,
        Интернет-магазин CLOTH
        """

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [order.user.email],
                fail_silently=False,
            )
            logger.info(f"Payment notification sent to {order.user.email}")
        except Exception as e:
            logger.error(f"Failed to send payment notification: {e}")

    def process_webhook(self, request_body):
        """
        Обработка webhook от ЮKassa

        Args:
            request_body: Тело запроса в JSON формате

        Returns:
            True в случае успеха, False при ошибке
        """
        try:
            # Получаем объект уведомления
            notification = WebhookNotification(request_body)
            event = notification.event
            payment = notification.object

            logger.info(f"Webhook received: {event} for payment {payment.id}")

            # Обрабатываем событие
            if event == 'payment.succeeded':
                self.handle_successful_payment(payment.id)
            elif event == 'payment.canceled':
                self.handle_failed_payment(payment.id)
            elif event == 'payment.waiting_for_capture':
                logger.info(f"Payment waiting for capture: {payment.id}")
                # Здесь можно автоматически подтвердить платеж
                # self.yookassa.capture_payment(payment.id)
            elif event == 'refund.succeeded':
                logger.info(f"Refund succeeded for payment {payment.id}")
                # Обработка возврата

            return True

        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return False
