from .base import *
from decouple import config

SECRET_KEY = 'django-insecure-cjog9l9qggjf*4at5xa5)h&n@aq_8!txjd*&+8knt7#4ec7$+4'

OSC_CLIENT_SECRET = 'xrhVmrn0CUb7fNv8tZKoCV/5h+Kf/AH85hPZZDMopMo='

OSC_CLIENT_ID = "3a21d9c1-bd7a-4ff1-9ccf-0700e40a57f8"

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DEV_DB_NAME'),
        'USER': config('DEV_DB_USER'),
        'PASSWORD': config('DEV_DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')