from django.conf.urls import include, url
from django.urls.conf import path
from rest_framework import routers
from common.views import get_businessunits, get_components_list, get_dashboard_incident_component_status, get_scheduled_maintenance_activity_list, get_sidebar_list, Mytemplates,get_status_page_incidents, get_statuspage_components_list,get_network_lists,subsciber_type_count,get_subscribers_component_list,get_sch_mnt_component_list

from common.viewsets import ComponentsViewset, IncidentTemplateViewset, IncidentsActivityViewset, IncidentsViewset, ScheduledMaintanenceViewset, SubscribersViewset


router = routers.DefaultRouter()
router.register(r"incidents", IncidentsViewset, basename="incidents")
router.register(r"components", ComponentsViewset, basename="components")
router.register(r"incident_activity_log", IncidentsActivityViewset)
router.register(r'subscribers',SubscribersViewset),
router.register(r"scheduled_maintanence",ScheduledMaintanenceViewset)
router.register(r'incident_template',IncidentTemplateViewset)

urlpatterns = [
    path(r'components/components_list', get_components_list),
    path(r'components/statuspage_components_list',get_statuspage_components_list),
    path(r'businessunits', get_businessunits),
    path(r'sidebar', get_sidebar_list),
    path(r'dashboard_incident', get_dashboard_incident_component_status),
    path(r'status_page_incidents',get_status_page_incidents),
    path('networks',get_network_lists),
    path("subscribers/subsciberscount",subsciber_type_count),
    path(r'subscribers/subscribercomponent',get_subscribers_component_list),
    path(r'scheduled_maintanence/activity_list',get_scheduled_maintenance_activity_list),
    path(r'scheduled_maintanence/components_list',get_sch_mnt_component_list),
    path('template', Mytemplates),
    url("", include(router.urls)),
]
