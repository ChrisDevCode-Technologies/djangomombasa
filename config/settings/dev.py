"""
Django development settings.

Use this for local development. Includes sensible defaults
that don't require environment variables to be set.

Usage:
    DJANGO_SETTINGS_MODULE=config.settings.dev python manage.py runserver
"""

from .base import *  # noqa: F401, F403

# SECURITY WARNING: keep the secret key used in production secret!
# This key is for development only - never use in production
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-only-key-do-not-use-in-production'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Development hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CSRF trusted origins for local development
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Use console email backend in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
