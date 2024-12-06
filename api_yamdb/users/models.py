from django.core.validators import EmailValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.constants import (
    MAX_LENGTH_USERNAME,
    MAX_LENGTH_EMAIL,
    USER_ROLES
)

USER = USER_ROLES['user']
ADMIN = USER_ROLES['admin']
MODERATOR = USER_ROLES['moderator']


class User(AbstractUser):
    """Модель пользователя."""

    roles = [*USER_ROLES.items()]

    username = models.CharField(
        verbose_name='Никнейм',
        max_length=MAX_LENGTH_USERNAME,
        unique=True
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=MAX_LENGTH_EMAIL,
        validators=[EmailValidator, ]
    )
    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=len(max(USER_ROLES.values(), key=len)),
        choices=roles,
        default='user'
    )
    bio = models.TextField(
        verbose_name='Bio',
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    def __str__(self):
        return self.username
