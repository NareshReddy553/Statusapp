import logging

from rest_framework.permissions import BasePermission

# logger = logging.getLogger("account.permissions")


class BaseStAppPermission(BasePermission):
    def check_permission(self, priv, request):
        user = request.user
        if user is None or user.privileges is None:
            return False
        # Root user can access all
        if "SystemAdmin" in user.privileges:
            return True
        return priv in user.privileges


class IsSystemAdmin(BaseStAppPermission):
    def has_permission(self, request, view):
        return self.check_permission("SystemAdmin", request)


class IsSecurityAdmin(BaseStAppPermission):
    def has_permission(self, request, view):
        return self.check_permission("SecurityAdmin", request)


class IsBusinessUnitUser(BaseStAppPermission):
    def has_permission(self, request, view):
        return self.check_permission("BusinessUnitUser", request)


class IsTestAdmin(BaseStAppPermission):
    def has_permission(self, request, view):
        return self.check_permission("TestAdmin", request)
