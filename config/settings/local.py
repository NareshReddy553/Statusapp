from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-1n3_3l4g3@w=m0v84a(pxhh4-hi2p#d&gk=7cm3b^=6cau2(^c"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "tsapp_dev",
        "USER": "tsapp_usr",
        "PASSWORD": "a6uK$X#o0135",
        "HOST": "18.118.80.163",
        "PORT": "3306",
        "OPTIONS": {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}
