from django.urls import path

from . import views

# App-level URL patterns.
#
# `config/urls.py` includes this file under the prefix "api/users/", so the
# paths below are relative to that prefix:
#
#   ""          -> /api/users/        (list + create)
#   "<int:id>/" -> /api/users/42/     (one user)
#
# The `<int:id>` part is a *path converter*: it matches digits only and hands
# the view `id` as a Python int. Use `<str:...>` for text or `<uuid:...>` for
# UUIDs. This is the Django equivalent of Express's `/users/:id`.
urlpatterns = [
    path("", views.user_list, name="user-list"),
    path("<int:id>/", views.user_detail, name="user-detail"),
]
