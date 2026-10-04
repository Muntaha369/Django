from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Registers the User model with Django's built-in admin site so you can browse
    and edit rows at /admin/ without writing any SQL.

    (Run `python manage.py createsuperuser` once to log in.)
    """

    list_display = ("id", "name", "email", "created_at")
    search_fields = ("name", "email")
