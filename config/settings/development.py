"""
Development settings for ecommerce project.
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = ['127.0.0.1']

# Development database (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable secure cookie flags in development
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Cache for development (in-memory)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ecommerce-dev',
    }
}

# CORS for development
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000',
]

# Celery configuration for development
CELERY_TASK_ALWAYS_EAGER = True  # Synchronous tasks in development
CELERY_TASK_EAGER_PROPAGATES = True
