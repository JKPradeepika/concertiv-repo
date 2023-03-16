import os
from datetime import timedelta

from pathlib import Path
from dotenv.main import dotenv_values
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# config from env
config = dotenv_values(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config["DEBUG"]

# list of strings representing the host/domain names that this Django site can serve
# This is a security measure to prevent HTTP Host header attacks,
# which are possible even under many seemingly-safe web server configurations
ALLOWED_HOSTS = config["ALLOWED_HOSTS"].split(",")

# list of trusted origins for unsafe requests (e.g.POST)
# For requests that include the Origin header, Django’s CSRF protection requires
# that header match the origin present in the Host header.
CSRF_TRUSTED_ORIGINS = config["CSRF_TRUSTED_ORIGINS"].split(",")

CORS_ORIGIN_WHITELIST = config["CORS_ORIGIN_WHITELIST"].split(",")

# Base URL (for Swagger or Internal App)
BASE_URL = config["BASE_URL"]

# Application definition
INSTALLED_APPS = [
    "api.apps.ApiConfig",  # first in list to override createsuperuser command
    "material",
    "material.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "drf_yasg",
    "django_filters",
    "phonenumber_field",
    "djmoney",
    "storages",
]

# Custom User
AUTH_USER_MODEL = "api.User"

# DRF Config
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        # "rest_framework.permissions.AllowAny",
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": (
        "api.helpers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10000,
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=30),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

# API Swagger Config
SWAGGER_SETTINGS = {"SECURITY_DEFINITIONS": {"Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}}}

ROOT_URLCONF = "komodo_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "komodo_backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DB_NAME = config["DB_NAME"]
DB_USER = config["DB_USER"]
DB_PASSWORD = config["DB_PASSWORD"]
DB_HOST = config["DB_HOST"]
DB_PORT = config["DB_PORT"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        "ATOMIC_REQUEST": True,
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

PHONENUMBER_DEFAULT_REGION = "US"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# SuperUser Config
SUPERUSER_EMAIL = config["SUPERUSER_EMAIL"]
SUPERUSER_FIRST_NAME = config["SUPERUSER_FIRST_NAME"]
SUPERUSER_LAST_NAME = config["SUPERUSER_LAST_NAME"]
SUPERUSER_PASSWORD = config["SUPERUSER_PASSWORD"]

# Material admin styling
MATERIAL_ADMIN_SITE = {
    "HEADER": _("Concertiv"),  # Admin site header
    "TITLE": _("Concertiv"),  # Admin site title
    # "FAVICON": "path/to/favicon",  # Admin site favicon (path to static should be specified)
    "MAIN_BG_COLOR": "#0D3A62",  # Admin site main color, css color should be specified
    "MAIN_HOVER_COLOR": "#008A69",  # Admin site main hover color, css color should be specified
    # "PROFILE_PICTURE": "path/to/image",  # Admin site profile picture (path to static should be specified)
    # "PROFILE_BG": "path/to/image",  # Admin site profile background (path to static should be specified)
    # "LOGIN_LOGO": "path/to/image",  # Admin site logo on login page (path to static should be specified)
    # "LOGOUT_BG": "path/to/image",  # Admin site background on login/logout pages (path to static should be specified)
    "SHOW_THEMES": False,  # Hide default admin themes button
    "TRAY_REVERSE": True,  # Hide object-tools and additional-submit-line by default
    "NAVBAR_REVERSE": True,  # Hide side navbar by default
    "SHOW_COUNTS": False,  # Hide instances counts for each model
    # Set icons for applications(lowercase), including 3rd party apps, {'application_name': 'material_icon_name', ...}
    "APP_ICONS": {
        "auth": "lock",
    },
}

# Django Storages Config (AWS S3) Ref: https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_S3_FILE_OVERWRITE = False
AWS_S3_ACCESS_KEY_ID = config["AWS_S3_ACCESS_KEY_ID"]
AWS_S3_SECRET_ACCESS_KEY = config["AWS_S3_SECRET_ACCESS_KEY"]
AWS_S3_REGION_NAME = config["AWS_S3_REGION_NAME"]
AWS_STORAGE_BUCKET_NAME = config["AWS_STORAGE_BUCKET_NAME"]
# CDN Cloudfront (use the same bucket name based on our custom configuration)
AWS_S3_CUSTOM_DOMAIN = AWS_STORAGE_BUCKET_NAME

EMAIL_BACKEND = config["EMAIL_BACKEND"]
EMAIL_HOST = config["EMAIL_HOST"]
EMAIL_HOST_USER = config["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = config["EMAIL_HOST_PASSWORD"]
EMAIL_PORT = config["EMAIL_PORT"]
EMAIL_USE_TLS = config["EMAIL_USE_TLS"]
