from datetime import datetime

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

from core.constants import MAX_LENGTH_USERNAME


def username_me(value):
    """Проверка имени пользователя (me недопустимое имя)."""
    if value == 'me':
        raise ValidationError(
            'Имя пользователя "me" не разрешено.'
        )
    return value


def validate_year(value):
    """Проверка даты."""
    if value >= datetime.now().year:
        raise ValidationError(
            message=f'Год {value} больше текущего!',
            params={'value': value},
        )


class UsernameRegexValidator(UnicodeUsernameValidator):
    """Валидация имени пользователя."""

    regex = r'^[\w.@+-]+\Z'
    flags = 0
    max_length = MAX_LENGTH_USERNAME
    message = (f'Введите правильное имя пользователя. Оно может содержать'
               f' только буквы, цифры и знаки @/./+/-/_.'
               f' Длина не более {MAX_LENGTH_USERNAME} символов')
    error_messages = {
        'invalid': f'Набор символов не более {MAX_LENGTH_USERNAME}. '
                   'Только буквы, цифры и @/./+/-/_',
        'required': 'Поле не может быть пустым',
    }
