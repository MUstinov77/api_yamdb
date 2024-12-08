from rest_framework.generics import get_object_or_404
from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    ValidationError,
    Serializer
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


from core.constants import MAX_LENGTH_USERNAME
from users.models import User


class UserCreateSerializer(ModelSerializer):
    """Cериализатор для обработки данных нового пользователя."""

    class Meta:
        model = User
        fields = (
            'username',
            'email'
        )

    def validate(self, attrs):
        if attrs.get('username') == 'me':
            raise ValidationError(
                'Этот ник нежелателен! Пожалуйста придумайте другой.'
            )
        elif User.objects.filter(username=attrs.get('username')):
            raise ValidationError(
                'Этот ник уже занят!'
            )
        elif User.objects.filter(email=attrs.get('email')):
            raise ValidationError(
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
            'role',
            'first_name',
            'last_name'
        )

    def validate(self, attrs):
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')
        if not first_name or not last_name:
            return attrs
        if len(first_name) > 150 or len(last_name) > 150:
            raise ValidationError(
                'Длинна имени и фамилии не должна превышать 150 символов!'
            )
        return attrs

    def validate_username(self, username):
        if username == 'me':
            raise ValidationError(
                'Это имя использовать запрещено!'
            )
        return username



class JWTSerializer(Serializer):
    """Сериализатор получения токена."""


    username = CharField(
        max_length=MAX_LENGTH_USERNAME,
        required=True
    )
    confirmation_code = CharField(
        max_length=150,
        required=True,
        write_only=True,
    )
