import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.core.cache import cache
from django.db.models import Prefetch
from rest_framework_simplejwt.authentication import (
    AuthenticationFailed,
    InvalidToken,
    JWTAuthentication,
    api_settings,
)

from common.models import UserBusinessunits

from .account_models import Role, RolesPrivs, Users, UsersPassword
from .utils import get_hashed_password

logger = logging.getLogger("account.backends")
user_cache_prefix = "USER_CACHE_"
role_cache = "ROLE_CACHE"


class UserBaseBackend:
    def get_role_dict(self):
        role_dict = cache.get(role_cache)
        if role_dict is None:
            logger.info("Loading all roles and their privileges to memory")
            all_roles = Role.objects.all().prefetch_related(
                Prefetch(
                    "privs", queryset=RolesPrivs.objects.select_related("priv"))
            )
            role_dict = {}
            for role in all_roles:
                privs = role.privs.all()
                priv_list = list()
                for priv in privs:
                    priv_list.append(priv.priv.priv_name)
                role_dict[role.role_name] = priv_list
            cache.set(role_cache, role_dict, None)
        return role_dict

    def prep_user(self, user):
        role_dict = self.get_role_dict()

        # get the UserProfile's roles
        user_roles = user.roles.all().select_related("role")
        priv_set = set()
        for user_role in user_roles:
            role_name = user_role.role.role_name
            privs = role_dict[role_name]
            priv_set.update(privs)

        user.privileges = tuple(priv_set)
        user.is_authenticated = True

        user_cache_name = user_cache_prefix + str(user.user_id)
        cache.set(user_cache_name, user, settings.USER_CACHE_TTL)

        return user


class AccountBackend(BaseBackend, UserBaseBackend):
    def authenticate(self, request, username, password, **kwargs):
        # 1. get UserProfile and UserPassword by username
        logger.debug("username: " + username)

        try:
            user = Users.objects.get(
                email__iexact=username,
                is_active=True,
                # login_attempts__lte=settings.LOGIN_ATTEMPTS,
            )
        except Users.DoesNotExist:
            return None

        if user is None:
            return None

        logger.debug("User ID: " + str(user.user_id))
        userPass = (
            UsersPassword.objects.filter(user=user)
            .order_by("-userpassword_id")
            .first()
        )

        # in case we don't need to populate a user's profile to django.contrib.auth.models.User, we can use following
        # simple query
        # userPass = UsersPasswords.objects.filter(user__username=username).order_by('-userpassword_id').first()

        if userPass is None:
            return None

        # 2. calculate password's hash
        pwdHash = get_hashed_password(password)

        # 3. compare UserPassword password hash and the calculated hash
        if pwdHash != userPass.password:
            # user.login_attempts = user.login_attempts + 1
            # user.save()
            return None

        if not user.is_active:
            raise AuthenticationFailed(
                _("User is inactive"), code="user_inactive")

        # 4. get the UserProfile's roles
        # reset login_attemps and last login time
        # user.login_attempts = 0
        user.lastlogin_date = datetime.now()
        user_bs_qs = UserBusinessunits.objects.filter(user=user).first()
        user.last_businessiunit_name = user_bs_qs.businessunit.businessunit_name
        user.save()
        return self.prep_user(user)


class AccountJWTAuthentication(JWTAuthentication, UserBaseBackend):
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(
                _("Token contained no recognizable user identification"))

        # use memory cache for better performance
        user_cache_name = user_cache_prefix + str(user_id)
        user = cache.get(user_cache_name)

        if user is None:
            try:
                user = Users.objects.get(pk=user_id)
            except Users.DoesNotExist:
                raise AuthenticationFailed(
                    _("User not found"), code="user_not_found")

            user = self.prep_user(user)
            if not user.is_active:
                raise AuthenticationFailed(
                    _("User is inactive"), code="user_inactive")

        return user
