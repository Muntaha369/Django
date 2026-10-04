from django.db import models


class User(models.Model):
    """
    A Django model is a Python class that maps to a database table.

    Django turns this class into a table named `users_user`
    (`<app_label>_<class_name lowercased>`). Each class attribute below becomes
    a column, and each `objects.create()/filter()` call becomes SQL.

    NOTE: this is a plain app model, NOT Django's built-in `auth.User`. We keep
    it deliberately tiny so the ORM is easy to read.
    """

    # `id` is not written here: Django adds an auto-incrementing primary key
    # (`id`) automatically. Every model gets one unless you declare your own.
    name = models.CharField(max_length=100)

    # EmailField is a CharField that also validates the address format.
    # unique=True adds a UNIQUE constraint in the database AND makes DRF's
    # ModelSerializer reject duplicate emails automatically.
    email = models.EmailField(unique=True)

    # auto_now_add=True sets the value once, when the row is first created.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Default ordering for every query, so listings are predictable.
        ordering = ["id"]

    def __str__(self) -> str:
        # Human-friendly label used by the admin site and the Django shell.
        return f"{self.name} <{self.email}>"
