# Generated by Django 3.2 on 2024-12-07 17:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Никнейм содержит недопустимые символы', regex='^[\\w.@+-]+$'), django.core.validators.MaxLengthValidator(limit_value=150, message='Длинна никнейма не должна превышать 150')], verbose_name='Никнейм'),
        ),
    ]
