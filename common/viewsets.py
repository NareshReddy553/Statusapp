import datetime

from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from account.utils import get_hashed_password
from django.db.models import Q
from django.db.models import Max

from common.models import Businessunits, Components, IncidentComponent, Incidents, IncidentsActivity, Smsgateway, SubcriberComponent, Subscribers,ComponentsStatus
from common.serializers import ComponentsSerializer, IncidentSerializer, IncidentsActivitySerializer, SubscribersSerializer
from common.utils import get_component_status
from common.mailer import send_email
from django.db import transaction


class IncidentsViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = IncidentSerializer

    def get_queryset(self):
        l_businessunit = self.request.headers.get('businessunit')
        queryset = Incidents.objects.filter(
            businessunit__businessunit_name=l_businessunit, is_active=True, isdeleted=False)
        return queryset

    @action(detail=True, methods=["put"], url_path="update_incident")
    def update_incident(self, request, pk=None):
        input_data = request.data
        new_components = input_data.get('components', None)
        uncheck_components = input_data.get('uncheck_component', None)
        l_incident = self.get_object()
        l_businessunit_name = request.headers.get(
            'businessunit')
        user = request.user
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True).first()
        l_incident.businessunit = businessunit_qs
        l_incident.modifieduser = user
        l_incident.modified_datetime = datetime.datetime.now()
        serializer = self.serializer_class(
            l_incident, input_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # inc_comp_obj = IncidentComponent.objects.filter(incident=pk)
            inc_comp_update = []
            inc_comp_create = []
            component_update = []
            l_incident_activity = []
            l_datetime = datetime.datetime.now()
            if new_components:

                for new_comp_obj in new_components:  # COmponets obj list
                    inc_comp_qs = IncidentComponent.objects.filter(
                        incident=pk, component=new_comp_obj.get('component_id')).first()
                    qs_component = Components.objects.get(
                        pk=new_comp_obj.get('component_id'))
                    l_status_id = get_component_status(
                        new_comp_obj.get('component_status'))
                    if inc_comp_qs:
                        # So we have the recor for this component and incident we need to do check weather status is changed or not
                        # status check
                        # If incident component object is inactive then we need to update that object
                        if not inc_comp_qs.is_active:
                            inc_comp_qs.is_active = True
                            inc_comp_qs.modify_datetime = l_datetime
                            inc_comp_update.append(inc_comp_qs)

                        if qs_component and not qs_component.component_status_id == l_status_id:  # if status not match
                            # Update components status if it is updated in incident
                            qs_component.modifieduser = request.user
                            qs_component.component_status_id = l_status_id
                            component_update.append(qs_component)

                    else:
                        # create a new object incident and update the status
                        inc_comp_create.append(IncidentComponent(
                            incident=l_incident, component_id=new_comp_obj.get('component_id'), is_active=True, created_datetime=l_datetime, modify_datetime=l_datetime, businessunit_id=businessunit_qs.pk))
                        if qs_component:
                            qs_component.modifieduser = request.user
                            qs_component.component_status_id = l_status_id
                            component_update.append(qs_component)

            if uncheck_components:
                for uncheck_comp_data in uncheck_components:
                    IncidentComponent.objects.filter(incident_id=pk, component_id=uncheck_comp_data['component_id']).update(
                        is_active=False, modify_datetime=l_datetime)

            if component_update:
                comp_obj = Components.objects.bulk_update(
                    component_update, fields=['modifieduser', 'component_status', ])
                for comp_data in component_update:
                    l_incident_activity.append(IncidentsActivity(
                        incident_id=l_incident.pk,
                        incident_name=l_incident.name,
                        message=l_incident.message,
                        status=l_incident.status,
                        businessunit_id=l_incident.businessunit_id,
                        component_id=comp_data.component_id,
                        component_name=comp_data.component_name,
                        component_status=comp_data.component_status.component_status_name,
                        component_status_id=comp_data.component_status.component_status_id,
                        createduser_id=user.user_id,
                        modifieduser_id=user.user_id,
                        created_datetime=datetime.datetime.now(),
                        modified_datetime=datetime.datetime.now()))
            if inc_comp_update:
                IncidentComponent.objects.bulk_update(
                    inc_comp_update, fields=['modify_datetime', 'is_active', ])
            if inc_comp_create:
                inc_cmp_obj = IncidentComponent.objects.bulk_create(
                    inc_comp_create)
                # Need entry in the incident activity table each time when we create the incident
                # if inc_cmp_obj:
                #     for inc_cmp_data in inc_cmp_obj:
                #         cmp_qs = Components.objects.filter(
                #             component_id=inc_cmp_data.component_id).first()
                #         l_incident_activity.append(IncidentsActivity(
                #             incident_id=l_incident.pk,
                #             incident_name=l_incident.name,
                #             message=l_incident.message,
                #             status=l_incident.status,
                #             businessunit_id=l_incident.businessunit_id,
                #             component_id=cmp_qs.component_id,
                #             component_name=cmp_qs.component_name,
                #             component_status=cmp_qs.component_status.component_status_name,
                #             component_status_id=cmp_qs.component_status.component_status_id,
                #             createduser_id=user.user_id,
                #             modifieduser_id=user.user_id,
                #             created_datetime=datetime.datetime.now(),
                #             modified_datetime=datetime.datetime.now()))
            if l_incident_activity:
                incident_activity_obj = IncidentsActivity.objects.bulk_create(
                    l_incident_activity)
            # send_email('index.html', None, 'test_email',
            #            ['naresh.gangireddy@data-axle.com'], [])
            # TODO need to send the mail

            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"], url_path="postmorterm")
    def postmorterm_incident(self, request, pk=None):
        input_data = request.data
        if input_data is None or input_data.get('incident_postmortem') is None:
            raise ValidationError(
                {
                    "incident_postmortem": "incident postmortem either in the payload or should not be None or empty string."
                }
            )
        l_incident = self.get_object()
        l_incident.modifieduser = request.user
        serializer = self.serializer_class(
            l_incident, input_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path="delete_incident")
    def delete_incident(self, request, pk=None):
        l_incident = self.get_object()
        try:
            # deleted_obj = Incidents.objects.filter(pk=pk).update(isdeleted=True,
            #  modifieduser=request.user, modify_datetime=datetime.datetime.now())
            l_incident.isdeleted = True
            l_incident.modifieduser = request.user
            l_incident.modify_datetime = datetime.datetime.now()
            l_incident.save()
            IncidentComponent.objects.filter(
                incident=l_incident,).update(is_active=False, modify_datetime=datetime.datetime.now())
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

    
        
        
class ComponentsViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Components.objects.all()
    serializer_class = ComponentsSerializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = {"component_name": {'in'}}
    def get_queryset(self):
        l_businessunit = self.request.headers.get('businessunit')
        queryset = Components.objects.filter(
            businessunit__businessunit_name=l_businessunit, is_active=True)
        return queryset 
        
    @action(detail=False, methods=["get"], url_path="group_components")
    def group_component(self, request, pk=None):
        queryset=self.get_queryset()
        queryset=queryset.filter(has_subgroup=True,is_group=True)
        serializer=self.serializer_class(queryset,many=True)
        if serializer.data:
            return Response(serializer.data,status=status.HTTP_200_OK)
        
    @action(detail=False, methods=["post"], url_path="create_component")
    def create_component(self, request, pk=None):
        input_data=request.data
        l_businessunit_name = request.headers.get(
            'businessunit')
        user = request.user
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True).first()
        #check for component and  grouptype
        if not input_data.get('component_name'):
            raise ValidationError({"Error":"Please provide component name"})
        component_create=[]
        if input_data.get('component_name') :
            cmp_orders=Components.objects.filter(businessunit=businessunit_qs).aggregate(Max('group_no'),Max('display_order'))
            l_ComponentsStatus=ComponentsStatus.objects.filter(component_status_name='Operational').first()
            if input_data.get('new_group_name'):
                new_group_name=input_data.get('new_group_name')
                # new group component  creation
                component_create.append(Components(component_name=new_group_name,
                                                   description="",
                                                   is_group=True,
                                                   group_no=int(cmp_orders['group_no__max'])+1,
                                                   display_order=int(cmp_orders['display_order__max'])+1,
                                                   subgroup_display_order=0,
                                                   businessunit=businessunit_qs,
                                                   createduser=user,
                                                   modifieduser=user,
                                                   has_subgroup=True,
                                                   component_status=l_ComponentsStatus
                                                   ))
                # new component creation from the new group component
                component_create.append(Components(component_name=input_data.get('component_name'),
                                                   description=input_data.get('description'),
                                                   is_group=False,
                                                   group_no=cmp_orders['group_no__max']+1,
                                                   display_order=cmp_orders['display_order__max']+1,
                                                   subgroup_display_order=1,
                                                   businessunit=businessunit_qs,
                                                   createduser=user,
                                                   modifieduser=user,
                                                   has_subgroup=False,
                                                   component_status=l_ComponentsStatus
                                                   ))

            elif input_data.get('group_component'):
                component_obj=Components.objects.get(pk=input_data.get('group_component'))
                l_subgroup_display_order=Components.objects.filter(group_no=component_obj.group_no,businessunit=businessunit_qs).aggregate(Max("subgroup_display_order"))
                component_create.append(Components(component_name=input_data.get('component_name'),
                                                   description=input_data.get('description'),
                                                   is_group=False,
                                                   group_no=component_obj.group_no,
                                                   display_order=component_obj.display_order,
                                                   subgroup_display_order=l_subgroup_display_order['subgroup_display_order__max']+1,
                                                   businessunit=businessunit_qs,
                                                   createduser=user,
                                                   modifieduser=user,
                                                   has_subgroup=False,
                                                   component_status=l_ComponentsStatus
                                                   ))
            else:
                
                component_create.append(Components(component_name=input_data.get('component_name'),
                                                   description=input_data.get('description'),
                                                   is_group=True,
                                                   group_no=cmp_orders['group_no__max']+1,
                                                   display_order=cmp_orders['display_order__max']+1,
                                                   subgroup_display_order=1,
                                                   businessunit=businessunit_qs,
                                                   createduser=user,
                                                   modifieduser=user,
                                                   has_subgroup=False,
                                                   component_status=l_ComponentsStatus
                                                   ))
        try:
            if component_create:
                Components.objects.bulk_create(
                    component_create)
                return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)   

            
        

    @action(detail=True, methods=["patch"], url_path="update_component")
    def update_component(self, request, pk=None):
        input_data = request.data
        l_component = self.get_object()
        l_businessunit_name = request.headers.get(
            'businessunit')
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True).first()
        try:
            if not l_component:
                raise ValidationError({"Error":"component not found in database please provide valid component id"})
            if l_component.is_group and l_component.has_subgroup:
                # Update the group component
                input_data["modifieduser"]=request.user.pk
                serializer = self.serializer_class(l_component,data=input_data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors,
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                # Update the sub group component
                if input_data.get('component_group'):
                    
                    group_component_qs=Components.objects.get(pk=input_data.get('component_group'))
                    if group_component_qs:
                        input_data["is_group"]=False
                        input_data["group_no"]=group_component_qs.group_no
                        input_data["display_order"]=group_component_qs.display_order
                        input_data["subgroup_display_order"]=Components.objects.filter(group_no=group_component_qs.group_no,businessunit=businessunit_qs).aggregate(Max("subgroup_display_order")).get('subgroup_display_order__max')+1
                        input_data["has_subgroup"]=False            
                input_data["modifieduser"]=request.user.pk
                serializer = self.serializer_class(l_component,data=input_data,partial=True)
                if serializer.is_valid():
                    # while updating the component if group component is changes then we need to look at the current updating component 
                    # which is under sub group and if the sub group is has only one sub component then we need to update  sub group to component
                    if input_data.get('component_group'):
                        l_component_count=Components.objects.filter(group_no=l_component.group_no,businessunit=businessunit_qs).count()
                        if l_component_count and l_component_count<=2:
                            group_component=Components.objects.filter(group_no=l_component.group_no,is_group=True,has_subgroup=True,businessunit=businessunit_qs).first()
                            if group_component:
                                group_component.subgroup_display_order=1
                                group_component.modifieduser=request.user
                                group_component.has_subgroup=False
                                group_component.save()
                    serializer.save()
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors,
                                    status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=["delete"], url_path="delete_component")
    def delete_component(self, request, pk=None):
        user=request.user
        l_component= self.get_object()
        l_businessunit_name = request.headers.get(
            'businessunit')
        user = request.user
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True).first()
        try:
            # check deleting object is group component or sub group component
            if l_component.is_group and l_component.has_subgroup:
                # if group component then we need to update the sub group componet which are belong to this group component as independent components
                sub_components_qs=Components.objects.filter(group_no=l_component.group_no,businessunit=businessunit_qs).filter(~Q(component_id=l_component.pk))
                if sub_components_qs:
                    counter=1
                    for qs in sub_components_qs:
                        
                        cmp_orders=Components.objects.filter(businessunit=businessunit_qs).aggregate(Max('group_no'),Max('display_order'))
                        if counter==1:
                            l_group=cmp_orders['group_no__max']
                            l_display_order=cmp_orders['display_order__max']
                        else:
                            l_group=int(cmp_orders['group_no__max'])+1
                            l_display_order=int(cmp_orders['display_order__max'])+1
                        # Update sub components
                        qs.is_group=1
                        qs.group_no=l_group
                        qs.display_order=l_display_order
                        qs.modifieduser=user
                        qs.subgroup_display_order=0,
                        qs.save()
                        counter+=1
            deleted_obj = l_component.delete()
            return Response(deleted_obj, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class IncidentsActivityViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = IncidentsActivitySerializer
    queryset = IncidentsActivity.objects.all()

    @action(detail=False, methods=["put"], url_path="incident_activity")
    def incident_activity_on_incident_id(self, request, pk=None):
        input_data = request.data
        if input_data is None or input_data.get('incident_id') is None:
            raise ValidationError(
                {
                    "incident_id": "incident id is required in payload."
                }
            )
        queryset = self.get_queryset()
        l_queryset = queryset.filter(
            incident_id=input_data.get('incident_id')).order_by("-modified_datetime")
        serializer = self.serializer_class(l_queryset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)



class SubscribersViewset(viewsets.ModelViewSet):
    serializer_class = SubscribersSerializer
    queryset = Subscribers.objects.all()
    
    @action(detail=False, methods=["post"], url_path="create_subscriber")
    def create_subsciber_on_businessunit(self, request, pk=None):
        serializer = self.serializer_class(
            data=request.data,context={"businessunit":self.request.headers.get('businessunit')}
        )
        if serializer.is_valid(raise_exception=True):
            l_serializer = serializer.create(serializer.validated_data)
            if l_serializer:
                return Response(status=status.HTTP_200_OK)
            else:
                return Response( status=status.HTTP_400_BAD_REQUEST)   