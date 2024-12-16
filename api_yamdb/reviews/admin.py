from django.contrib import admin
from django.contrib.admin import display

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title
)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'year', 'description', 'get_genre')
    search_fields = ('name', 'description')
    list_filter = ('category', 'genre')
    list_editable = ('category',)

    @display(description='Жанр(ы)')
    def get_genre(self, obj):
        """Получает жанр или список жанров произведения."""
        return ', '.join((genre.name for genre in obj.genre.all()))


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'score', 'pub_date')
    search_fields = ('title__name', 'author__username', 'text')
    list_filter = ('score',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'author', 'pub_date')
    search_fields = ('review__title__name', 'author__username', 'text')
