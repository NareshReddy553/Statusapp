from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from account.permissions import IsBusinessUnitUser

from common.models import Businessunits, Components, Sidebar, UserBusinessunits
from account.permissions import BaseStAppPermission
from common.utils import component_group_order

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
    finaldata_list = list()
    queryset = Components.objects.select_related().filter(
        businessunit__businessunit_name=request.headers.get('businessunit'), businessunit__is_active=True)
    groups_qa = queryset.filter(is_group=True)
    subgroup_qs = queryset.filter(is_group=False)
    for query in groups_qa:
        local_list = list()
        local_final_dict = component_group_order(query)
        for subgp_data in subgroup_qs:
            local_temp_dict = dict()
            if query.group_no == subgp_data.group_no:
                local_temp_dict = component_group_order(subgp_data)
                local_list.append(local_temp_dict)
        local_final_dict['sub_component'] = local_list
        finaldata_list.append(local_final_dict)
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


def Mytemplates(request):
    return render(request, 'index.html')
