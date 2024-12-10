from django.core.mail import send_mail

from api_yamdb.settings import EMAIL_ADMIN

from .constants import subject


def send_confirmation_code(email, code):
    send_mail(
        subject=subject,
        message=f'Код подтверждения: {code}',
        from_email=EMAIL_ADMIN,
        recipient_list=(email,),
        fail_silently=False,
    )
