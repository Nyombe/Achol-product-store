"""
Production settings for ecommerce project.
"""

from .base import *
import dj_database_url
from whitenoise.storage import CompressedManifestStaticFilesStorage

DEBUG = False

# This must be set properly in production
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='.onrender.com,achol-fashion-store.onrender.com', cast=Csv())

# Database Configuration - Serverless PostgreSQL (Neon) for Production
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=''),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}

# HTTPS & Security
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static and Media files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_KEEP_ONLY_HASHED_FILES = True

MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

# Cache with Redis (Fallback to LocMem if REDIS_URL is missing)
REDIS_URL = config('REDIS_URL', default=None)
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'PARSER_KWARGS': {'encoding': 'utf8'},
            },
            'KEY_PREFIX': 'ecommerce',
            'TIMEOUT': 300,
        }
    }

# CORS
CORS_ALLOWED_ORIGINS = [
    "https://achol-fashion-store.onrender.com",
]
