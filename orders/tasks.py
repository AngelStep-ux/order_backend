# tasks.py
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

@shared_task
def send_order_confirmation_email(order_id):
    from backend.models import Order
    try:
        order = Order.objects.get(id=order_id)
        context = {'order': order}
        html_content = render_to_string('emails/order_confirmation.html', context)

        email = EmailMultiAlternatives(
            subject='Ваш заказ подтвержден',
            body='Ваш заказ успешно подтвержден.',
            from_email='email@example.ru',
            to=[order.user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Order.DoesNotExist:
        pass