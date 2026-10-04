"""
Django settings for the `config` project.

This file is the single place where the whole project is configured: the
database, the installed apps, the middleware chain, third-party packages, and
so on. Reading it top to bottom tells you what the project is made of.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# BASE_DIR is the folder that contains manage.py (the project root).
BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from a local .env file (if present) into os.environ, so the
# values below can read them. `.env` is gitignored; `.env.example` documents
# which variables exist. This is where SECRET_KEY/DEBUG come from.
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    """Read a boolean environment variable, e.g. DEBUG=True."""
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


# SECURITY WARNING: keep the secret key secret in production!
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-only-change-me")

# DEBUG=True shows detailed error pages. Never enable it in production.
DEBUG = env_bool("DEBUG", default=True)

# Hosts allowed to serve this app. Comma-separated in the environment.
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]


# --- Application definition -------------------------------------------------

# INSTALLED_APPS is how the project learns which apps exist. Each string is a
# Python import path (or an AppConfig) that Django loads at startup.
INSTALLED_APPS = [
    # Django's built-in apps (admin, auth, sessions, ...).
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps.
    "rest_framework",  # Django REST Framework
    # Local apps -- our own code. ONE app for this project: `users`.
    "users",
]

# MIDDLEWARE is an ordered list. A request passes through each item (top to
# bottom) on the way in, then back up (bottom to top) on the way out.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Our own middleware (see users/middleware.py). It logs each request.
    # Placed last so it wraps the view as tightly as possible.
    "users.middleware.RequestLoggingMiddleware",
]

# The "root URLconf": the file where URL resolution starts for every request.
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Entry points used by WSGI/ASGI servers (and by the dev server).
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# --- Database ---------------------------------------------------------------
# SQLite keeps this project dependency-free: no server to install or run.
# `NAME` is just a file in the project root.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# --- Authentication (only used by Django's built-in auth app) ---------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# --- Internationalization ---------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# --- Static files -----------------------------------------------------------
STATIC_URL = "static/"


# --- Misc -------------------------------------------------------------------
# Type used for auto-created primary keys (`id`) when a model does not declare
# one. BigAutoField is a 64-bit integer (rendered as a normal JSON number).
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email backend (unused here, but harmless and useful if you add email later).
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}


# --- Django REST Framework --------------------------------------------------
# These are GLOBAL defaults; an individual view can override them with the
# @authentication_classes / @permission_classes decorators.
REST_FRAMEWORK = {
    # How a caller proves who they are.
    #   - SessionAuthentication: used by the browsable API / logged-in admin.
    #   - BasicAuthentication: convenient for curl/Postman.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    # Who is allowed to use the endpoints.
    #   AllowAny        -> public (what we use here)
    #   IsAuthenticated -> must be logged in
    # Change the line below to require authentication across the whole API.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}


# --- Logging ----------------------------------------------------------------
# Makes the custom middleware's log lines appear in the runserver console.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        # Any logger whose name starts with "users." (e.g. "users.request")
        # writes to the console at INFO level.
        "users": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
