from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Every Django app has an AppConfig. Django uses it to discover the app and
    to attach metadata to it.

    This class is what `INSTALLED_APPS = [..., "users"]` points at: when Django
    sees "users" it imports `users.apps.UsersConfig` automatically.
    """

    # The type used for auto-created primary keys (`id`) when a model does not
    # declare one. Django 5+ prefers the 64-bit BigAutoField.
    default_auto_field = "django.db.models.BigAutoField"

    # The Python package/import path of the app.
    name = "users"
