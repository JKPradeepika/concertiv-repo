from .base import *
from decouple import config

SECRET_KEY = 'django-insecure-ziqerb$y8639i16l%r%^q3!gu+y-lgwxln6xjd!4r@(%y+hi01'

CLIENT_SECRET='N7nXOGHQf8MrKaC0qthpxYa04vXikQMw7OrHfhyMS7Q='

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('QA_DB_NAME'),
        'USER': config('QA_DB_USER'),
        'PASSWORD': config('QA_DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
