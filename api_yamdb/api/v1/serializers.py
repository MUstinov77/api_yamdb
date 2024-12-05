from rest_framework.serializers import ModelSerializer, Serializer, CharField

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


class GetTokenSerializer(Serializer):
    """Сериализатор получения токена."""

    username = CharField(
        max_length=MAX_LENGTH_USERNAME,
        required=True
    )
    confirmation_code = CharField(
        required=True
    )
