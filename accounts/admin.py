from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Expose the custom role field in the Django admin."""

    fieldsets = UserAdmin.fieldsets + (("CMS role", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("CMS role", {"fields": ("role",)}),)
    list_display = ("username", "email", "role", "is_staff")
    list_filter = UserAdmin.list_filter + ("role",)
