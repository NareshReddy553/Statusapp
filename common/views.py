from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from account.permissions import IsBusinessUnitUser

from common.models import Businessunits, Components, ComponentsStatus, IncidentsActivity, Sidebar, UserBusinessunits
from account.permissions import BaseStAppPermission
from common.utils import component_group_order, get_components_all_list

# Create your views here.


@api_view(["GET"])
@permission_classes([IsAuthenticated, ])
def get_businessunits(request):
    """
     This api will return the Businessunits based on the privileges and and access of the user to that Businessunit.
    """
    rst = {}
    priv = request.user.privileges
    if "SystemAdmin" in request.user.privileges:
        businessunits = Businessunits.objects.values_list(
            'businessunit_name', flat=True)
    else:
        businessunits = UserBusinessunits.objects.select_related().filter(
            allow_access=True, user=request.user).values_list('Businessunit__name', flat=True)

    rst['BusinessUnits'] = businessunits
    return Response(rst, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_components_list(request):
    """ 
        This API is to get the list of components based on the businessunit,display order and group number
    """
    queryset = Components.objects.select_related().filter(
        businessunit__businessunit_name=request.headers.get('businessunit'), businessunit__is_active=True)
    finaldata_list = get_components_all_list(queryset)

    return Response(finaldata_list, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_sidebar_list(request):
    """ 
        This API is to get the list of components based on the businessunit,display order and group number
    """
    queryset = Sidebar.objects.filter(
        businessunit__businessunit_name=request.headers.get('businessunit')).values()
    sidebar_list = []
    for query in queryset:
        sidebar_list.append(query.get('sidebar_name'))
    if "SystemAdmin" not in request.user.privileges:
        sidebar_list.remove('Security')
    return Response(sidebar_list, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_dashboard_incident_component_status(request):
    l_business_unit = Businessunits.objects.filter(
        businessunit_name=request.headers.get('businessunit')).first().businessunit_id
    component_status_incident = []
    l_status_list = ComponentsStatus.objects.values_list(
        'component_status_name', flat=True)
    if l_status_list:
        for l_status in l_status_list:
            status_dict = {}
            l_IncidentsActivity = IncidentsActivity.objects.filter(
                component_status=l_status, businessunit_id=l_business_unit).order_by('-modified_datetime').first()
            if l_IncidentsActivity:
                status_dict['incident_id'] = l_IncidentsActivity.incident_id
                status_dict['component_status'] = l_IncidentsActivity.component_status
                status_dict['component_id'] = l_IncidentsActivity.component_id
                component_status_incident.append(status_dict)
    return Response(component_status_incident, status=status.HTTP_200_OK)


def Mytemplates(request):
    return render(request, 'index.html')
