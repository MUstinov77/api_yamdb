from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    validate_slug
)
from django.db import models

from reviews.validators import validate_year
from core.constants import (
    LENG_SLUG,
    LENG_MAX,
    LENG_CUT,
    MIN_SCORE,
    MAX_SCORE
)
from users.models import User


class BaseGenreAndCategoryModel(models.Model):
    """
    Абстрактная модель.

    Добавляет уникальный slug и название.
    """

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

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.CharField(
        'Текст',
        max_length=LENG_MAX
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


class Category(BaseGenreAndCategoryModel):
    """Модель категории произведения."""

    class Meta(BaseGenreAndCategoryModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        default_related_name = 'categories'

    def __str__(self):
        return self.name


class Genre(BaseGenreAndCategoryModel):
    """Модель жанра произведений."""

    class Meta(BaseGenreAndCategoryModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        default_related_name = 'genres'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведения."""

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
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.PROTECT,
        related_name='titles',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(BaseAuthorModel):
    """Модель отзыва произведения."""

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
        default=1,
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
