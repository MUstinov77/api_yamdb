from django.contrib import admin
from reviews.models import *


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'year', 'description')
    search_fields = ('name', 'description')
    list_filter = ('category', 'genre')


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
