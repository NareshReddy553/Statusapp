from .base_settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-1n3_3l4g3@w=m0v84a(pxhh4-hi2p#d&gk=7cm3b^=6cau2(^c"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "aware247",
        "USER": "aware247",
        "PASSWORD": "Aware!247!sTatus",
        "HOST": "aware247.cdnwv8kjmo3k.us-east-1.rds.amazonaws.com",
        "PORT": "3306",
        "OPTIONS": {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=400),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "user_id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=120),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.office365.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "status@data-axle.com"
EMAIL_HOST_PASSWORD = "YN@ADsLWv4T$*1"
DEFAULT_FROM_EMAIL = "status@data-axle.com"

UNSUBSCRIBE_URL = (
    "http://54.235.41.120:80/Status/{l_businessunit_name}/unsubscribe/{token}"
)
MANAGE_SUBSCRIBER_URL = (
    "http://54.235.41.120:80/Status/{l_businessunit_name}/manage/{subscriber_Hash_id}"
)

STATUS_PUBLIC_URL = "http://54.235.41.120:80/Status/{l_businessunit_name}"

LOGIN_URL = "http://54.235.41.120:80"
