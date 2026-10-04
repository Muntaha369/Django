from typing import Any

from .models import User

# The service layer is where *business logic* lives.
# Views handle HTTP (parse input, pick a status code); services talk to the ORM.
# Keeping it here means the same logic can be reused by views, management
# commands, tests, background jobs, etc. -- and it stays unit-testable.


def list_users(name: str | None = None, email: str | None = None):
    """
    Return users, optionally filtered by the given query parameters.

    The view passes the raw query-param values through; this layer decides what
    they mean. Returns a QuerySet, which is lazy: the SQL runs only when the
    serializer iterates over it.
    """
    queryset = User.objects.all()  # `all()` == "SELECT * FROM users_user"

    if name is not None:
        # `name__iexact` = case-insensitive exact match on the `name` column.
        # The double underscore is Django ORM's "lookup" syntax.
        queryset = queryset.filter(name__iexact=name)

    if email is not None:
        queryset = queryset.filter(email__iexact=email)

    return queryset


def get_user(user_id: int) -> User:
    """
    Fetch a single user by primary key.

    Raises `User.DoesNotExist` when there is no matching row. The view catches
    that and turns it into an HTTP 404 -- keeping HTTP concerns out of here.
    """
    return User.objects.get(pk=user_id)


def create_user(validated_data: dict[str, Any]) -> User:
    """
    Create and save a user, then return the saved model instance.

    `validated_data` comes from `serializer.validated_data`, so by the time we
    get here the data has already been validated.
    """
    return User.objects.create(**validated_data)
