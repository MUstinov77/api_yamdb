from django.core.validators import EmailValidator
from django.contrib.auth.models import AbstractUser
from django.db import models


class CommonUser(AbstractUser):
    username = models.CharField(
        verbose_name='Никнейм',
        max_length=50,
        unique=True
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=100,
        validators=[EmailValidator,]
    )
    role = models.CharField(
        verbose_name='Роль пользователя',
        choices=...,
        default='user',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('nickname',)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    def __str__(self):
        return self.username[:10]


