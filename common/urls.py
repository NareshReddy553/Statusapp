from django.conf.urls import include, url
from django.urls.conf import path
from rest_framework import routers
from common.views import get_businessunits, get_components_list, get_dashboard_incident_component_status, get_sidebar_list, Mytemplates,get_status_page_incidents, get_statuspage_components_list,get_network_lists

from common.viewsets import ComponentsViewset, IncidentsActivityViewset, IncidentsViewset, SubscribersViewset


router = routers.DefaultRouter()
router.register(r"incidents", IncidentsViewset, basename="incidents")
router.register(r"components", ComponentsViewset, basename="components")
router.register(r"incident_activity_log", IncidentsActivityViewset)
router.register(r'subscribers',SubscribersViewset)
urlpatterns = [
    path(r'components/components_list', get_components_list),
    path(r'components/statuspage_components_list',get_statuspage_components_list),
    path(r'businessunits', get_businessunits),
    path(r'sidebar', get_sidebar_list),
    path(r'dashboard_incident', get_dashboard_incident_component_status),
    path(r'status_page_incidents',get_status_page_incidents),
    path('networks',get_network_lists),
    path('template', Mytemplates),
    url("", include(router.urls)),
]
