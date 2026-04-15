"""
KekiCakes – Base Settings
Shared across all environments
"""

import pymysql
# Spoof version to satisfy Django 6's mysqlclient >= 2.2.1 check
pymysql.version_info = (2, 2, 1, 'final', 0)
pymysql.install_as_MySQLdb()

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'insecure-dev-key-change-me')
DEBUG = True
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,kekicakes.co.ke,www.kekicakes.co.ke').split(',')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    # Local apps
    'apps.core',
    'apps.products',
    'apps.orders',
    'apps.payments',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kekicakes.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'kekicakes.wsgi.application'

# ── Database (MySQL via PyMySQL) ──────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'kekicakes_db'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ── Auth & Passwords ───────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ───────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# ── Static & Media ─────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── M-Pesa / Daraja ───────────────────────────────────────────────────────────
DARAJA_ENVIRONMENT = os.getenv('DARAJA_ENVIRONMENT', 'sandbox')
DARAJA_CONSUMER_KEY = os.getenv('DARAJA_CONSUMER_KEY', '')
DARAJA_CONSUMER_SECRET = os.getenv('DARAJA_CONSUMER_SECRET', '')
DARAJA_SHORTCODE = os.getenv('DARAJA_SHORTCODE', '174379')
DARAJA_PASSKEY = os.getenv('DARAJA_PASSKEY', '')
DARAJA_CALLBACK_URL = os.getenv('DARAJA_CALLBACK_URL', 'https://kekicakes.co.ke/payments/mpesa/callback/')

# ── WhatsApp ──────────────────────────────────────────────────────────────────
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER', '254726613651')

# ── Cart Session Key ──────────────────────────────────────────────────────────
CART_SESSION_ID = 'kekicakes_cart'

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'mail.kekicakes.co.ke')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 465))
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'True').lower() in ('true', '1', 't')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# ── Jazzmin Admin Layout ──────────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title": "Keki Cakes Admin",
    "site_header": "Keki Cakes",
    "site_brand": "Keki Cakes",
    # "site_logo": "images/logo.png", # add if we have an exact path
    "welcome_sign": "Welcome to the Keki Cakes Management Portal",
    "copyright": "Keki Cakes",
    "search_model": ["auth.User", "orders.Order"],
    "show_ui_builder": False,
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Site", "url": "/", "new_window": True},
    ],
    "usermenu_links": [
        {"model": "auth.user"}
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "products.Category": "fas fa-tags",
        "products.Cake": "fas fa-birthday-cake",
        "products.CakeVariant": "fas fa-cubes",
        "orders.Customer": "fas fa-address-book",
        "orders.Order": "fas fa-shopping-cart",
        "payments.MpesaTransaction": "fas fa-money-bill-wave",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
}

JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-white navbar-light",
    "theme": "litera",
    "sidebar": "sidebar-dark-maroon",
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme_color": "maroon",
    "accent": "accent-maroon",
    "actions_sticky_top": False
}
