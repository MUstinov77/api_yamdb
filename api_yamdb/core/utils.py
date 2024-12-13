from django.core.mail import send_mail

from api_yamdb.settings import EMAIL_ADMIN
from .constants import CONFIRM_CODE_MESSAGE


def send_confirmation_code(email, code):
    send_mail(
        subject=CONFIRM_CODE_MESSAGE,
        message=f'Код подтверждения: {code}',
        from_email=EMAIL_ADMIN,
        recipient_list=(email,),
        fail_silently=False,
    )
