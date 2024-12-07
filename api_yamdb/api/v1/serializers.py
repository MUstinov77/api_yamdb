from rest_framework.generics import get_object_or_404
from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    ValidationError,
    RegexField,
    DateTimeField,
    IntegerField,
    SlugRelatedField
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.constants import MAX_LENGTH_USERNAME
from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    Comment
)
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


class JWTSerializer(TokenObtainPairSerializer):
    """Сериализатор получения токена."""

    username = CharField(
        max_length=MAX_LENGTH_USERNAME,
        required=True
    )
    confirmation_code = CharField(
        max_length=150,
        required=True,
    )
    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['email'] = self.user.email
        return data


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
    """Базовый сериализатор произведения."""

    class Meta:
        model = Title
        fields = '__all__'


class TitleGetSerializer(TitleSerializer):
    """Сериализатор для получения произведений."""

    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = IntegerField(read_only=True)


class TitleEditSerializer(TitleSerializer):
    """Сериализатор для изменения произведений."""

    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="slug",
    )
    genre = SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field="slug",
        many=True,
    )


class ReviewSerializer(ModelSerializer):
    """Сериализатор отзыва."""

    author = SlugRelatedField(
        read_only=True, slug_field='username'
    )
    pub_date = DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)

    class Meta:
        model = Review
        exclude = ('title',)

    def validate(self, data):
        request = self.context.get('request')
        if request.method != 'POST':
            return data
        view = self.context.get('view')
        title = get_object_or_404(
            Title, pk=view.kwargs.get('title_id')
        )
        if title.reviews.filter(author=request.user).exists():
            raise ValidationError(
                'Можно оставить только один отзыв для одного произведения!'
            )
        return data


class CommentSerializer(ModelSerializer):
    """Сериализатор комментария."""

    author = SlugRelatedField(
        read_only=True, slug_field='username'
    )
    pub_date = DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)

    class Meta:
        model = Comment
        exclude = ('review',)
