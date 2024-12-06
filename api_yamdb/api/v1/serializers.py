from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    ValidationError,
RegexField
)

from core.constants import MAX_LENGTH_USERNAME
from users.models import User


class SignUpSerializer(ModelSerializer):
    """Cериализатор для обработки данных нового пользователя."""

    class Meta:
        model = User
        fields = (
            'username',
            'email'
        )

    def validate(self, attrs):
        if attrs.get('username') == 'me':
            return ValidationError(
                'Этот ник нежелателен! Пожалуйста придумайте другой.'
            )
        elif User.objects.get(username=attrs.get('username')):
            return ValidationError(
                'Этот ник уже занят!'
            )
        elif User.objects.get(email=attrs.get('email')):
            return ValidationError(
                'Пользователь с таким email уже существует!'
            )
        return attrs


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'bio',
            'role'
        )

    def validate_username(self, username):
        if username == 'me':
            return ValidationError(
                'Это имя использовать запрещено!'
            )
        return username



class GetTokenSerializer(Serializer):
    """Сериализатор получения токена."""

    username = CharField(
        max_length=MAX_LENGTH_USERNAME,
        required=True
    )
    confirmation_code = CharField(
        required=True
    )


