from django.conf.urls import include, url
from django.urls.conf import path
from rest_framework import routers

from common.views import (
    get_businessunits,
    get_components_list,
    get_dashboard_incident_component_status,
    get_incident_impact_list,
    get_network_lists,
    get_sch_mnt_component_list,
    get_scheduled_maintenance_activity_list,
    get_sidebar_list,
    get_status_page_incidents,
    get_status_page_sch_mnt_incidents,
    get_statuspage_components_list,
    get_subscribers_component_list,
    subsciber_type_count,
)
from common.viewsets import (
    BusinessunitViewset,
    ComponentsViewset,
    IncidentsActivityViewset,
    IncidentsViewset,
    IncidentTemplateViewset,
    ScheduledMaintanenceViewset,
    SubscribersViewset,
)

router = routers.DefaultRouter()
router.register(r"incidents", IncidentsViewset, basename="incidents")
router.register(r"components", ComponentsViewset, basename="components")
router.register(r"incident_activity_log", IncidentsActivityViewset)
router.register(r"subscribers", SubscribersViewset),
router.register(r"scheduled_maintanence", ScheduledMaintanenceViewset)
router.register(r"incident_template", IncidentTemplateViewset)
router.register(r"businessunit", BusinessunitViewset)

urlpatterns = [
    path(r"components/components_list", get_components_list),
    path(r"components/statuspage_components_list", get_statuspage_components_list),
    path(r"businessunits", get_businessunits),
    path(r"sidebar", get_sidebar_list),
    path(r"dashboard_incident", get_dashboard_incident_component_status),
    path(r"status_page_incidents", get_status_page_incidents),
    path(
        r"scheduled_maintanence/status_page_sch_mnt_inc",
        get_status_page_sch_mnt_incidents,
    ),
    path("networks", get_network_lists),
    path("subscribers/subsciberscount", subsciber_type_count),
    path(r"subscribers/subscribercomponent", get_subscribers_component_list),
    path(
        r"scheduled_maintanence/activity_list", get_scheduled_maintenance_activity_list
    ),
    path(r"scheduled_maintanence/components_list", get_sch_mnt_component_list),
    path(r"incidents/impact_list", get_incident_impact_list),
    url("", include(router.urls)),
]
