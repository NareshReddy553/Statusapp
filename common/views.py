import datetime

from dateutil.relativedelta import relativedelta
from django import get_version
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.http import is_safe_url
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import Users
from common.models import (
    Businessunits,
    CommonLookups,
    Components,
    ComponentsStatus,
    IncidentComponent,
    Incidents,
    IncidentsActivity,
    ScheduledMaintenance,
    SchMntActivity,
    SchMntComponent,
    Sidebar,
    Smsgateway,
    SubcriberComponent,
    Subscribers,
    UserBusinessunits,
)

# from account.permissions import BaseStAppPermission
from common.serializers import (
    IncidentsActivitySerializer,
    IncidentSerializer,
    ScheduledMaintanenceSerializer,
    SchMntActivitySerializer,
    StatusPageIncidentsSerializer,
)
from common.utils import  get_components_all_list

@api_view(["GET"])
@permission_classes(
    [
        IsAuthenticated,
    ]
)
def get_businessunits(request):
    """
    This api will return the Businessunits based on the privileges and and access of the user to that Businessunit.
    """
    rst = {}
    businessunits = Businessunits.objects.filter(is_active=True).values_list(
        "businessunit_name", flat=True
    )
    rst["BusinessUnits"] = businessunits
    return Response(rst, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_components_list(request):
    """
    This API is to get the list of components based on the businessunit,display order and group number.
    """
    queryset = Components.objects.select_related().filter(
        businessunit__businessunit_name=request.headers.get("businessunit"),
        businessunit__is_active=True,
    )
    finaldata_list = get_components_all_list(queryset)

    return Response(finaldata_list, status=status.HTTP_200_OK)


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_statuspage_components_list(request):
    """
    This API is to get the list of components based on the businessunit,display order and group number.
    """
    queryset = Components.objects.select_related().filter(
        businessunit__businessunit_name=request.headers.get("businessunit"),
        businessunit__is_active=True,
    )
    if queryset:
        # raise ValidationError({"Error":"Businessunit not found or inactive, Please provide active businessunit"})
        finaldata_list = get_components_all_list(queryset)

        return Response(finaldata_list, status=status.HTTP_200_OK)
    else:
        error = {
            "Error": "Businessunit not found or inactive, Please provide active businessunit"
        }
        return Response(error, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_sidebar_list(request):
    """
    This API is to get the list of components based on the businessunit,display order and group number.

    """
    queryset = Sidebar.objects.filter(
        is_active=True,
    ).values()
    sidebar_list = []
    for query in queryset:
        sidebar_list.append(query.get("sidebar_name"))
    return Response(sidebar_list, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_dashboard_incident_component_status(request):
    l_business_unit = (
        Businessunits.objects.filter(
            businessunit_name=request.headers.get("businessunit")
        )
        .first()
        .businessunit_id
    )
    component_status_incident = []
    component_qs = Components.objects.filter(
        is_active=True, businessunit_id=l_business_unit, has_subgroup=False
    )
    if component_qs:
        for component_data in component_qs:
            status_dict = {}
            incident_component_obj = (
                IncidentComponent.objects.filter(
                    component_id=component_data.component_id,
                    businessunit_id=l_business_unit,
                    is_active=True,
                    incident__isdeleted=False,
                    incident__is_active=True,
                )
                .order_by("-modify_datetime")
                .first()
            )
            if incident_component_obj:
                status_dict["component_id"] = incident_component_obj.component_id
                status_dict["component_name"] = component_data.component_name
                status_dict[
                    "component_status"
                ] = component_data.component_status.component_status_name
                status_dict["incident_id"] = incident_component_obj.incident_id
                component_status_incident.append(status_dict)
    return Response(component_status_incident, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_status_page_incidents(request):
    """
    This api is used to get the all the incident with in the time period of 3 months.
    """
    start_date = datetime.datetime.now()
    end_date = start_date - relativedelta(months=3)
    l_businessunit = request.headers.get("businessunit")
    # queryset = IncidentsActivity.objects.filter(
    #     businessunit__businessunit_name=l_businessunit, incident__is_active=True, incident__isdeleted=False,created_datetime__gte=end_date)
    incident_qs = Incidents.objects.filter(
        businessunit__businessunit_name=l_businessunit,
        is_active=True,
        isdeleted=False,
        created_datetime__gte=end_date,
    )
    serializer = StatusPageIncidentsSerializer(incident_qs, many=True)
    if serializer:
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_status_page_sch_mnt_incidents(request):
    """
    This api is used to get the all the scheduled maintenance incident with in the time period of 3 months.
    """
    start_date = datetime.datetime.now()
    end_date = start_date - relativedelta(months=3)
    l_businessunit = request.headers.get("businessunit")
    queryset = SchMntActivity.objects.filter(
        sch_inc__businessunit__businessunit_name=l_businessunit,
        sch_inc__is_active=True,
        created_datetime__gte=end_date,
    )

    serializer = SchMntActivitySerializer(queryset, many=True)
    if serializer:
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_network_lists(request):
    network_list = Smsgateway.objects.values_list("network", flat=True)
    return Response(network_list, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subsciber_type_count(request):
    data = []
    l_business_unit = (
        Businessunits.objects.filter(
            businessunit_name=request.headers.get("businessunit")
        )
        .first()
        .businessunit_id
    )
    l_email_subscriber = Subscribers.objects.filter(
        businessunit=l_business_unit, email_delivery=True
    ).count()
    l_sms_subsciber = Subscribers.objects.filter(
        businessunit=l_business_unit, sms_delivery=True
    ).count()
    data = [{"email_subscibers": l_email_subscriber, "sms_subscibers": l_sms_subsciber}]
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_subscribers_component_list(request):
    components_list = []
    user_token = request.GET.get("id")
    l_business_unit = (
        Businessunits.objects.filter(
            businessunit_name=request.headers.get("businessunit")
        )
        .first()
        .businessunit_id
    )
    if user_token:

        subscriber = Subscribers.objects.filter(
            subscriber_token=user_token, businessunit=l_business_unit
        ).first()
        if not subscriber:
            raise ValidationError({"Error": "Susbscriber not found"})
        component = SubcriberComponent.objects.filter(
            subscriber=subscriber, businessunit=l_business_unit, is_active=True
        ).values_list("component_id", flat=True)
        if component:
            components_list = [{"component_id": component}]
        return Response(components_list, status=status.HTTP_200_OK)
    return Response(components_list)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_scheduled_maintenance_activity_list(request):
    sch_mnt_act_list = []
    sch_mnt_id = request.GET.get("id")
    if sch_mnt_id:
        sch_mnt_activity = SchMntActivity.objects.filter(sch_inc_id=sch_mnt_id)
        if not sch_mnt_activity:
            raise ValidationError({"Error": "scheduled maintenance activity not found"})
        serializer = SchMntActivitySerializer(sch_mnt_activity, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(sch_mnt_act_list, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_sch_mnt_component_list(request):
    components_list = []
    sch_mnt_id = request.GET.get("id")
    if sch_mnt_id:
        component = SchMntComponent.objects.filter(
            sch_inc_id=sch_mnt_id, is_active=True
        ).values_list("component_id", flat=True)
        if component:
            components_list = [{"component_id": component}]
        return Response(components_list, status=status.HTTP_200_OK)
    return Response(components_list)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_incident_impact_list(request):
    impact_severity = []
    impact_severity = CommonLookups.objects.filter(
        is_active=True, category="Incidents", sub_caterogy="impact_severity"
    ).values_list("looup_value", flat=True)
    return Response(impact_severity)
