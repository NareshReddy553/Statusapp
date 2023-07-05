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

SAML2_AUTH = {
    "METADATA_AUTO_CONF_URL": "https://data-axle.okta.com/app/exk9ghz03toIWmfjj5d7/sso/saml/metadata",
    "DEFAULT_NEXT_URL": "/",
    "CREATE_USER": "False",
    "ATTRIBUTES_MAP": {
        "email": "Email",
        "username": "UserName",
        "first_name": "FirstName",
        "last_name": "LastName",
        "role": "role",
    },
    "ASSERTION_URL": "http://18.118.80.163:8080",  # Custom URL to validate incoming SAML requests against
    "ENTITY_ID": "http://18.118.80.163:8080/saml2_auth/acs/",  # Populates the Issuer element in authn request
    "NAME_ID_FORMAT": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",  # Sets the Format property of authn NameIDPolicy element
    "USE_JWT": True,  # Set this to True if you are running a Single Page Application (SPA) with Django Rest Framework (DRF), and are using JWT authentication to authorize client users
    "FRONTEND_URL": "http://18.118.80.163/admin/dashboard",  # Redirect URL for the client if you are using JWT auth with DRF. See explanation below
}

UNSUBSCRIBE_URL = (
    "http://18.118.80.163/Status/{l_businessunit_name}/unsubscribe/{token}"
)
MANAGE_SUBSCRIBER_URL = (
    "http://18.118.80.163/Status/{l_businessunit_name}/manage/{subscriber_Hash_id}"
)
