import datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from account.permissions import IsBusinessUnitUser

from common.models import Businessunits, Components, ComponentsStatus, IncidentComponent, Incidents, IncidentsActivity, Sidebar, Smsgateway, UserBusinessunits
from account.permissions import BaseStAppPermission
from common.serializers import IncidentSerializer
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
# @permission_classes([IsAuthenticated])
def get_statuspage_components_list(request):
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
    component_qs = Components.objects.filter(
        is_active=True, businessunit_id=l_business_unit, has_subgroup=False)
    if component_qs:
        for component_data in component_qs:
            status_dict = {}
            incident_component_obj = IncidentComponent.objects.filter(
                component_id=component_data.component_id, businessunit_id=l_business_unit, is_active=True, incident__isdeleted=False, incident__is_active=True,).order_by('-modify_datetime').first()
            if incident_component_obj:
                status_dict['component_id'] = incident_component_obj.component_id
                status_dict['component_name'] = component_data.component_name
                status_dict['component_status'] = component_data.component_status.component_status_name
                status_dict['incident_id'] = incident_component_obj.incident_id
                component_status_incident.append(status_dict)
    return Response(component_status_incident, status=status.HTTP_200_OK)



@api_view(["GET"])
def get_status_page_incidents(request):
    """
        This api is used to get the all the incident with in the time period of 3 months
    """
    start_date=datetime.datetime.now()
    end_date=start_date-relativedelta(months=3)
    l_businessunit =request.headers.get('businessunit')
    queryset = Incidents.objects.filter(
        businessunit__businessunit_name=l_businessunit, is_active=True, isdeleted=False,modify_datetime__gte=end_date)

    serializer=IncidentSerializer(queryset,many=True)
    if serializer:
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
        


@api_view(["GET"])
def get_network_lists(request):
    network_list=Smsgateway.objects.values_list('network',flat=True)
    return Response(network_list,status=status.HTTP_200_OK)


def Mytemplates(request):
    l_incident = Incidents.objects.first()
    components_effected = ['adobe', 'import', 'export', 'yesmail marketing']
    l_status = str(l_incident.status).capitalize()
    context = {
        "incident_data": l_incident,
        "component_data": components_effected,
        "user": 'naresh.gangireddy@data-axle.com',
        "status": l_status,
        "name": l_incident.name,
        "message": l_incident.message
    }

    subject = f"[Data Axle platform status updates] Incident {l_status} - Admin"
    return render(request, template_name='subscriber_email_notification.html', context=context,)
    # return render(request, template_name='start.html', context=context)
