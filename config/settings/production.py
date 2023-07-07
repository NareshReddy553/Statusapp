from decouple import Csv, config

from .base import *

SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": config("ENGINE"),
        "NAME": config("NAME"),
        "USER": config("USER"),
        "PASSWORD": config("PASSWORD"),
        "HOST": config("HOST"),
        "PORT": config("PORT", cast=int),
        "OPTIONS": {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}

SAML2_AUTH = {
    "METADATA_AUTO_CONF_URL": config("METADATA_AUTO_CONF_URL"),
    "DEFAULT_NEXT_URL": "/",
    "CREATE_USER": "False",
    "ATTRIBUTES_MAP": {
        "email": "Email",
        "username": "UserName",
        "first_name": "FirstName",
        "last_name": "LastName",
        "role": "role",
    },
    "ASSERTION_URL": "https://status-api.data-axle.com",  # Custom URL to validate incoming SAML requests against
    "ENTITY_ID": "https://status-api.data-axle.com/saml2_auth/acs/",  # Populates the Issuer element in authn request
    "NAME_ID_FORMAT": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",  # Sets the Format property of authn NameIDPolicy element
    "USE_JWT": True,  # Set this to True if you are running a Single Page Application (SPA) with Django Rest Framework (DRF), and are using JWT authentication to authorize client users
    "FRONTEND_URL": "https://status-app.data-axle.com/admin/dashboard",  # Redirect URL for the client if you are using JWT auth with DRF. See explanation below
}

UNSUBSCRIBE_URL = (
    "https://status-app.data-axle.com/Status/{l_businessunit_name}/unsubscribe/{token}"
)
MANAGE_SUBSCRIBER_URL = "https://status-app.data-axle.com/Status/{l_businessunit_name}/manage/{subscriber_Hash_id}"

EMAIL_BACKEND = config("EMAIL_BACKEND")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")
