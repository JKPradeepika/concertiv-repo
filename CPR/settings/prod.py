from .base import *
from decouple import config
import secrets

SECRET_KEY = secrets.token_hex(16)

DEBUG = False

ALLOWED_HOSTS = ['concertiv-cpr.herokuapp.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('PROD_DB_NAME'),
        'USER': config('PROD_DB_USER'),
        'PASSWORD': config('PROD_DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}