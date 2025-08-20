from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail


def send_activation_email(request, user):
    current_site = get_current_site(request)
    domain = current_site.domain

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    token = default_token_generator.make_token(user)

    activation_path = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
    activation_link = f"http://{domain}{activation_path}"

    send_mail(
        'Подтверждение регистрации',
        f'Перейдите по ссылке для подтверждения: {activation_link}',
        'alina.step@mail.ru',
        [user.email],
        fail_silently=False,
    )