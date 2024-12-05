from django.core.validators import EmailValidator
from django.contrib.auth.models import AbstractUser
from django.db import models


class CommonUser(AbstractUser):
    nickname = models.CharField(
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
    role = models.CharField(...)
