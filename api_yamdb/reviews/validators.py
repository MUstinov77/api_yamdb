from datetime import datetime
from django.core.exceptions import ValidationError


def validate_year(value):
    """Проверка даты."""
    if value >= datetime.now().year:
        raise ValidationError(
            message=f'Год {value} больше текущего!',
            params={'value': value},
        )
