from django.db import models
from django.core.exceptions import ValidationError

MIN_SCORE = 1
MAX_SCORE = 10

def validate_score(score):
    """Проверка оценки."""
    if (score < MIN_SCORE) or (score > MAX_SCORE):
        raise ValidationError(
            f'Оценка должна быть в диапазоне от {MIN_SCORE} до {MAX_SCORE}.'
        )

class BaseAuthorModel(models.Model):
    """ 
    Абстрактная модель.
    Базовая модель с автором (author), текстом (text) и 
    датой (pub_date) для отзыва (Review) и комментария (Comment).
    """

    # Нужна модель юзера
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        )
    
    text = models.TextField(
        verbose_name='Текст',
        )
    
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.text


class Review(BaseAuthorModel):
    """
    Отзыв к произведению.
    """

    # Нужна модель произведения
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
        )
    score = models.PositiveSmallIntegerField(
        validators=[validate_score],
        verbose_name='Оценка',
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                )
        ]


class Comment(BaseAuthorModel):
    """
    Комментарий к отзыву.
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
