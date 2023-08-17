from django.conf.urls import include, url
from django.urls.conf import path
from rest_framework import routers
from account.views import ChangePasswordView, ResetPasswordRequestView, user_profile
from account.viewsets import UsersViewset
from common.views import get_businessunits, get_components_list

from common.viewsets import ComponentsViewset, IncidentsViewset


router = routers.DefaultRouter()
router.register(r"profile", UsersViewset, basename="users")

urlpatterns = [
    path(r'userprofile', user_profile),
    path("password/reset/", ResetPasswordRequestView.as_view()),
    path("password/change/", ChangePasswordView.as_view()),
    # path(r'update_businessunit', get_businessunits),
    url("", include(router.urls)),
]
