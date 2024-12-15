from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from core.constants import (
    FORBIDDEN_SIMBOLS_REGEX,
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_USERNAME,
    USER_ROLES
)
from core.validators import username_validator

USER = USER_ROLES['user']
ADMIN = USER_ROLES['admin']
MODERATOR = USER_ROLES['moderator']


class User(AbstractUser):
    """Модель пользователя."""

    roles = [*USER_ROLES.items()]

    username = models.CharField(
        verbose_name='Никнейм',
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[
            RegexValidator(
                regex=FORBIDDEN_SIMBOLS_REGEX,
                message='Никнейм содержит недопустимые символы',
            ),
            username_validator,
        ]
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=MAX_LENGTH_EMAIL,
    )
    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=len(max(USER_ROLES.values(), key=len)),
        choices=roles,
        default=USER
    )
    bio = models.TextField(
        verbose_name='Bio',
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser
