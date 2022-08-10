from .settings import *
import os

os.environ["ENV"] = "production"

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'concertiv-cpr.herokuapp.com']