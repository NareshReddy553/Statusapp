import urllib.error
import urllib.parse
import urllib.parse as _urlparse
import urllib.request as _urllib
from urllib.parse import unquote
import datetime
from django import get_version
from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.utils.http import is_safe_url
from django.views.decorators.csrf import csrf_exempt
from django_saml2_auth.views import (
    _create_new_user,
    _get_metadata,
    denied,
    get_current_domain,
)
from pkg_resources import parse_version
from rest_auth.utils import jwt_encode
from rest_framework.response import Response
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT, entity
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config

from account.account_models import Users
from common.models import Businessunits

User = get_user_model()


if parse_version(get_version()) >= parse_version("1.7"):
    from django.utils.module_loading import import_string
else:
    from django.utils.module_loading import import_by_path as import_string


def signin(r):

    next_url = r.GET.get("next", settings.SAML2_AUTH.get("DEFAULT_NEXT_URL", ""))
    try:
        if "next=" in unquote(next_url):
            next_url = _urlparse.parse_qs(_urlparse.urlparse(unquote(next_url)).query)[
                "next"
            ][0]
    except:
        next_url = r.GET.get("next", settings.SAML2_AUTH.get("DEFAULT_NEXT_URL"))

    # Only permit signin requests where the next_url is a safe URL
    if parse_version(get_version()) >= parse_version("2.0"):
        url_ok = is_safe_url(next_url, None)
    else:
        url_ok = is_safe_url(next_url)

    if not url_ok:
        return None

    r.session["login_next_url"] = next_url

    saml_client = _get_saml_client(get_current_domain(r))
    _, info = saml_client.prepare_for_authenticate()

    redirect_url = None

    for key, value in info["headers"]:
        if key == "Location":
            redirect_url = value
            break

    return redirect_url


def _get_saml_client(domain):
    acs_url = domain + get_reverse([acs, "acs", "django_saml2_auth:acs"])
    metadata = _get_metadata()

    saml_settings = {
        "metadata": metadata,
        "service": {
            "sp": {
                "endpoints": {
                    "assertion_consumer_service": [
                        (acs_url, BINDING_HTTP_REDIRECT),
                        (acs_url, BINDING_HTTP_POST),
                    ],
                },
                "allow_unsolicited": True,
                "authn_requests_signed": False,
                "logout_requests_signed": True,
                "want_assertions_signed": True,
                "want_response_signed": False,
            },
        },
    }

    if "ENTITY_ID" in settings.SAML2_AUTH:
        saml_settings["entityid"] = settings.SAML2_AUTH["ENTITY_ID"]

    if "NAME_ID_FORMAT" in settings.SAML2_AUTH:
        saml_settings["service"]["sp"]["name_id_format"] = settings.SAML2_AUTH[
            "NAME_ID_FORMAT"
        ]

    spConfig = Saml2Config()
    spConfig.load(saml_settings)
    spConfig.allow_unknown_attributes = True
    saml_client = Saml2Client(config=spConfig)
    return saml_client


def get_reverse(objs):
    """In order to support different django version, I have to do this."""
    if parse_version(get_version()) >= parse_version("2.0"):
        from django.urls import reverse
    else:
        from django.core.urlresolvers import reverse
    if objs.__class__.__name__ not in ["list", "tuple"]:
        objs = [objs]

    for obj in objs:
        try:
            return reverse(obj)
        except:
            pass
    raise Exception(
        "We got a URL reverse issue: %s. This is a known issue but please still submit a ticket at https://github.com/fangli/django-saml2-auth/issues/new"
        % str(objs)
    )


@csrf_exempt
def acs(r):
    saml_client = _get_saml_client(get_current_domain(r))
    resp = r.POST.get("SAMLResponse", None)
    next_url = r.session.get(
        "login_next_url", settings.SAML2_AUTH.get("DEFAULT_NEXT_URL")
    )

    if not resp:
        return HttpResponseRedirect(
            get_reverse([denied, "denied", "django_saml2_auth:denied"])
        )

    authn_response = saml_client.parse_authn_request_response(
        resp, entity.BINDING_HTTP_POST
    )
    if authn_response is None:
        return HttpResponseRedirect(
            get_reverse([denied, "denied", "django_saml2_auth:denied"])
        )

    user_identity = authn_response.get_identity()
    if user_identity is None:
        return HttpResponseRedirect(
            get_reverse([denied, "denied", "django_saml2_auth:denied"])
        )

    user_email = user_identity[
        settings.SAML2_AUTH.get("ATTRIBUTES_MAP", {}).get("email", "Email")
    ][0]
    user_name = user_identity[
        settings.SAML2_AUTH.get("ATTRIBUTES_MAP", {}).get("username", "UserName")
    ][0]
    user_first_name = user_identity[
        settings.SAML2_AUTH.get("ATTRIBUTES_MAP", {}).get("first_name", "FirstName")
    ][0]
    user_last_name = user_identity[
        settings.SAML2_AUTH.get("ATTRIBUTES_MAP", {}).get("last_name", "LastName")
    ][0]

    target_user = None
    is_new_user = False

    try:
        target_user = User.objects.get(username=user_name)
        ##################################################
        # check this user in ur database
        # create or update the user
        db_user = Users.objects.get(email=target_user.email)
        businessunit_obj=Businessunits.objects.filter(is_active=True)
        if not db_user:
            Users.objects.create(
                email=target_user.email,
                firstname=target_user.first_name,
                last_name=target_user.last_name,
                is_active=target_user.is_active,
                last_businessiunit_name=businessunit_obj[0].businessunit_name
            )
        db_user.lastlogin_date= datetime.datetime.now()
        if not db_user.last_businessiunit_name:
            db_user.last_businessiunit_name=businessunit_obj[0].businessunit_name
        db_user.save()
        #######################################################
        if settings.SAML2_AUTH.get("TRIGGER", {}).get("BEFORE_LOGIN", None):
            import_string(settings.SAML2_AUTH["TRIGGER"]["BEFORE_LOGIN"])(user_identity)
    except User.DoesNotExist:
        new_user_should_be_created = settings.SAML2_AUTH.get("CREATE_USER", True)
        if new_user_should_be_created:
            target_user = _create_new_user(
                user_name, user_email, user_first_name, user_last_name
            )
            if settings.SAML2_AUTH.get("TRIGGER", {}).get("CREATE_USER", None):
                import_string(settings.SAML2_AUTH["TRIGGER"]["CREATE_USER"])(
                    user_identity
                )
            is_new_user = True
        else:
            return HttpResponseRedirect(
                get_reverse([denied, "denied", "django_saml2_auth:denied"])
            )

    r.session.flush()

    if target_user.is_active:
        target_user.backend = "django.contrib.auth.backends.ModelBackend"
        login(r, target_user)
    else:
        return HttpResponseRedirect(
            get_reverse([denied, "denied", "django_saml2_auth:denied"])
        )

    if settings.SAML2_AUTH.get("USE_JWT") is True:
        # We use JWT auth send token to frontend
        jwt_token = jwt_encode(target_user)
        query = "?uid={}&token={}".format(target_user.id, jwt_token)

        frontend_url = settings.SAML2_AUTH.get("FRONTEND_URL", next_url)

        return HttpResponseRedirect(frontend_url + query)

    if is_new_user:
        try:
            return render(r, "django_saml2_auth/welcome.html", {"user": r.user})
        except TemplateDoesNotExist:
            return HttpResponseRedirect(next_url)
    else:
        return HttpResponseRedirect(next_url)
