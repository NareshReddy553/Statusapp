import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _


def email_validate(value):
    user_regex = _lazy_re_compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
        re.IGNORECASE,
    )
    try:
        validate_email(value)
        return True
    except Exception as e:
        raise ValidationError({"Error": "'Enter a valid recipient email address."})
