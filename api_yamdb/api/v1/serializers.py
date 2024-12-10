from rest_framework.generics import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
    Serializer,
    DateTimeField,
    SlugRelatedField
)


from reviews.validators import UsernameRegexValidator, username_me
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
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')


class JWTSerializer(Serializer):
    """Сериализатор получения токена."""

    username = serializers.CharField(
        required=True,
        validators=(UsernameRegexValidator(), )
    )
    confirmation_code = serializers.CharField(required=True)

    def validate_username(self, value):
        return username_me(value)


class CategorySerializer(ModelSerializer):
    """Сериализатор категории."""

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'


class GenreSerializer(ModelSerializer):
    """Сериализатор жанра."""

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'


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


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title
