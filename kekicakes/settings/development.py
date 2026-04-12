"""KekiCakes – Development Settings"""
from .base import *
from decouple import config

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# ── SQLite fallback for local development without MySQL ───────────────────────
# Set USE_SQLITE=True in your .env to skip MySQL
import os
if config('USE_SQLITE', default='False', cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db_dev.sqlite3',
        }
    }

# Show emails in console during development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
