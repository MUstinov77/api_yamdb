from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.constants import ADDITIONAL_USER_FIElDS
from .models import User


@admin.register(User)
class AdminUser(BaseUserAdmin):
    model = User

    add_fieldsets = BaseUserAdmin.add_fieldsets + ADDITIONAL_USER_FIElDS
    fieldsets = BaseUserAdmin.fieldsets + ADDITIONAL_USER_FIElDS

