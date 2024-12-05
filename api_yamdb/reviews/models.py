from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    validate_slug
)
from django.db import models
from .validators import UsernameRegexValidator, username_me, validate_year


LENG_SLUG = 50
LENG_MAX = 256
LENG_DATA_USER = 150
LENG_EMAIL = 254
LENG_CUT = 30
MIN_SCORE = 1
MAX_SCORE = 10


class BaseGenreAndCategoryModel(models.Model):
    """Добавляет уникальный slug и название."""

    slug = models.SlugField(
        'Slug',
        max_length=LENG_SLUG,
        unique=True,
        validators=[validate_slug],
    )
    name = models.CharField(
        'Название',
        max_length=LENG_MAX,
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:LENG_CUT]


class BaseAuthorModel(models.Model):
    """
    Абстрактная модель.

    Базовая модель с автором (author), текстом (text) и
    датой публикации (pub_date).
    """

    text = models.CharField(
        'Текст',
        max_length=LENG_MAX
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:LENG_CUT]


class User(AbstractUser):

    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
    )

    username = models.CharField(
        'Имя пользователя',
        validators=(UsernameRegexValidator(), username_me),
        max_length=LENG_DATA_USER,
        unique=True,
        blank=False,
        null=False,
        help_text=f'Набор символов не более {LENG_DATA_USER}.'
        'Только буквы, цифры и @/./+/-/_',
        error_messages={
            'unique': "Пользователь с таким именем уже существует!",
        },
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=LENG_EMAIL,
        unique=True,
        blank=False,
        null=False
    )
    role = models.CharField(
        'Роль',
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )

    REQUIRED_FIELDS = ('email', )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email',
            )
        ]

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    def __str__(self):
        return f'{self.username} {self.email} {self.role}'


class Category(BaseGenreAndCategoryModel):
    """Модель категории произведения."""

    class Meta(BaseGenreAndCategoryModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        default_related_name = 'categories'


class Genre(BaseGenreAndCategoryModel):
    """Модель жанра произведений."""

    class Meta(BaseGenreAndCategoryModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        default_related_name = 'genres'


class Title(models.Model):
    """Модель произведения."""

    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.PROTECT,
        related_name='titles',
    )
    description = models.TextField(
        'Описание',
        db_index=True,
        max_length=LENG_MAX,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        related_name='titles',
    )
    name = models.CharField(
        'Название',
        max_length=LENG_MAX,
        db_index=True,
    )
    year = models.PositiveSmallIntegerField(
        'Год выпуска',
        db_index=True,
        validators=(validate_year,),
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(BaseAuthorModel):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        db_index=True,
        validators=(
            MinValueValidator(MIN_SCORE),
            MaxValueValidator(MAX_SCORE)
        ),
        error_messages={
            'validators': f'Оценка от {MIN_SCORE} до {MAX_SCORE}!'
        },
        default=1
    )

    class Meta(BaseAuthorModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique_review',
            )
        ]


class Comment(BaseAuthorModel):
    """Модель комментария к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )

    class Meta(BaseAuthorModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
