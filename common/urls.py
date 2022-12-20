from django.conf.urls import include, url
from django.urls.conf import path
from rest_framework import routers
from common.views import get_businessunits, get_components_list, get_sidebar_list

from common.viewsets import ComponentsViewset, IncidentsViewset


router = routers.DefaultRouter()
router.register(r"incidents", IncidentsViewset, basename="incidents")
router.register(r"components", ComponentsViewset, basename="components")

urlpatterns = [
    path(r'components/components_list', get_components_list),
    path(r'businessunits', get_businessunits),
    path(r'sidebar', get_sidebar_list),
    url("", include(router.urls)),
]
