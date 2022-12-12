from django.conf.urls import include, url
from django.urls.conf import path
from rest_framework import routers
from account.views import user_profile
from account.viewsets import UsersViewset
from common.views import get_businessunits, get_components_list

from common.viewsets import ComponentsViewset, IncidentsViewset


router = routers.DefaultRouter()
# router.register(r"profile", UsersViewset, basename="users")

urlpatterns = [
    path(r'userprofile', user_profile),
    # path(r'businessunits', get_businessunits),
    url("", include(router.urls)),
]
