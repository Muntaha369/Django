"""
The root URLconf: URL resolution starts here for every incoming request.

`urlpatterns` is checked top to bottom. This file stays small on purpose: it
delegates ("includes") each area of the API to the URLconf of the app that owns
it. That is the same idea as mounting a router in Express:

    app.use("/api/users", usersRouter)
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django's built-in admin site.
    path("admin/", admin.site.urls),

    # Everything starting with "api/users/" is handled by the `users` app.
    # include() strips that prefix and passes the REST of the path to
    # users/urls.py, which then matches it against that app's own patterns.
    path("api/users/", include("users.urls")),
]
