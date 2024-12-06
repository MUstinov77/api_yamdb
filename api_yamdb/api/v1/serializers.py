from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    ValidationError,
    RegexField,
    DateTimeField,
    IntegerField
)

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
            'first_name',
            'last_name',
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

    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = IntegerField(read_only=True)
    
    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(ModelSerializer):
    """Сериализатор отзыва."""

    pub_date = DateTimeField(format='%Y-%m-%dT%H:%M:%SZ')

    class Meta:
        model = Review
        exclude = ('title',)


class CommentSerializer(ModelSerializer):
    """Сериализатор комментария."""

    pub_date = DateTimeField(format='%Y-%m-%dT%H:%M:%SZ')

    class Meta:
        model = Comment
        exclude = ('review',)
