from django.contrib import admin

from .models import User


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'bio',
    )
    list_editable = ('role',)
    list_filter = ('role',)
    search_fields = (
        'username',
        'email'
    )
