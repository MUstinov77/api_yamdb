from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    SlugRelatedField,
    ValidationError
)

from core.constants import (
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_USERNAME,
    RATING_DEFAULT_VALUE
)
from core.utils import send_confirmation_code
from core.validators import (
    UsernameRegexValidator,
    username_validator
)
from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title
)
from users.models import User


class UserCreateSerializer(ModelSerializer):
    """Cериализатор для обработки данных нового пользователя."""

    username = serializers.CharField(
        required=True,
        max_length=MAX_LENGTH_USERNAME,
        validators=(
            UsernameRegexValidator(),
            username_validator,
        )
    )
    email = serializers.EmailField(
        required=True,
        max_length=MAX_LENGTH_EMAIL
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email'
        )

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        confirmation_code = default_token_generator.make_token(user)
        send_confirmation_code(
            email=user.email,
            code=confirmation_code
        )
        return user

    def validate(self, attrs):
        if User.objects.filter(**attrs).exists():
            return attrs
        for attr_name, attr_value in attrs.items():
            if User.objects.filter(**{attr_name: attr_value}).exists():
                raise ValidationError(
                    f'Пользователь с {attr_name} уже существует.'
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


class JWTSerializer(Serializer):
    """Сериализатор получения токена."""

    username = serializers.CharField(
        required=True,
        validators=(UsernameRegexValidator(),)
    )
    confirmation_code = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        user = get_object_or_404(
            User,
            username=username
        )
        if not default_token_generator.check_token(
            user,
            token=attrs.get('confirmation_code')
        ):
            raise serializers.ValidationError(
                'Неверный код подтверждения.'
            )
        if not username_validator(username):
            raise serializers.ValidationError(
                'Неверное имя пользователя.'
            )
        return attrs


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


class ReviewSerializer(ModelSerializer):
    """Сериализатор отзыва."""

    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

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
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        exclude = ('review',)


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(
        read_only=True,
        default=RATING_DEFAULT_VALUE
    )

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
        many=True,
        allow_empty=False,
    )

    class Meta:
        fields = '__all__'
        model = Title

    def to_representation(self, instance):
        return TitleReadSerializer(instance).data
