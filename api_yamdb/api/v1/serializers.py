from rest_framework.serializers import ModelSerializer, Serializer, CharField

from core.constants import MAX_LENGTH_USERNAME
from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    Comment
)
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


class CategorySerializer(ModelSerializer):
    """Сериализатор категории."""

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(ModelSerializer):
    """Сериализатор жанра."""

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(ModelSerializer):
    """Сериализатор произведения."""
    
    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(ModelSerializer):
    """Сериализатор отзыва."""

    class Meta:
        model = Review
        exclude = ('title',)


class CommentSerializer(ModelSerializer):
    """Сериализатор комментария."""

    class Meta:
        model = Comment
        exclude = ('review',)


class UserSerializer(ModelSerializer):
    """Сериализатор пользователя."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            # Нужно поле bio
            # 'bio',
            'role',
        )