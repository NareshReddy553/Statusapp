import datetime
from django.forms import ValidationError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from common.models import Businessunits, Components, IncidentComponent, Incidents
from common.serializers import ComponentsSerializer, IncidentSerializer
from common.utils import get_component_status


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
            l_incident, input_data)
        if serializer.is_valid():
            serializer.save()
            # inc_comp_obj = IncidentComponent.objects.filter(incident=pk)
            inc_comp_update = []
            inc_comp_create = []
            component_update = []
            l_datetime = datetime.datetime.now()
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

                    if qs_component and not qs_component.component_status_id == l_status_id:  # if status not match
                        # Update components status if it is updated in incident
                        qs_component.modifieduser = request.user
                        qs_component.component_status_id = l_status_id
                        component_update.append(qs_component)

                else:
                    # create a new object incident and uodate the status
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
            if inc_comp_create:
                IncidentComponent.objects.bulk_create(inc_comp_create)
            if component_update:
                Components.objects.bulk_update(
                    component_update, fields=['modifieduser', 'component_status', ])

            # TODO need to send the mail

            # for inc_comp_obj_data in inc_comp_obj:#components incident obj
            #     for new_comp_obj in new_components:# COmponets obj list
            #         for new_comp_obj_data in new_comp_obj: #components obj dict
            #             if inc_comp_obj_data.pk == new_comp_obj_data.component_id:# if component is already is present need to update it

            #                 for status_data in status_list:
            #                     l_status_id = status_data.get(
            #                         new_comp_obj_data.component_status)
            #                     if l_status_id:
            #                         break
            #                 l_status_id = new_comp_obj_data.component_status
            #                 qs_component = Components.objects.get(
            #                     pk=new_comp_obj_data.component_id)
            #                 if qs_component and not qs_component.component_status == l_status_id:
            #                     # Update components status if it is updated in incident
            #                     qs_component.modifieduser = request.user
            #                     qs_component.component_status = l_status_id
            #                     component_update.append(qs_component)

            #                 # Update the incident_component table
            #                 qs_inccomp = IncidentComponent.objects.filter(incident=pk,
            #                                                               component=new_comp_obj_data.component_id)
            #                 qs_inccomp.is_active = True
            #                 qs_component.modify_datetime = datetime.datetime.now()
            #                 inc_comp_update.append(IncidentComponent(
            #                     is_active=True, component=new_comp_obj_data.component_id, modify_datetime=datetime.datetime.now()))

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

    # def get_queryset(self):
    #     # project_id may be None
    #     print(self.request.GET.get('businessunit'))
    #     print(self.request.GET.getlist('businessunit'))
    #     return self.queryset \
    #         .filter(businessunit__businessunit_name__in=self.request.GET.get('businessunit'))

    @action(detail=True, methods=["put"], url_path="update_incident")
    def update_incident(self, request, pk=None):
        input_data = request.data
        l_incident = self.get_object()
        serializer = self.serializer_class(data=input_data)
        if serializer.is_valid():
            l_incident.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path="delete_incident")
    def delete_incident(self, request, pk=None):
        input_data = request.data
        l_incident = self.get_object()
        try:
            deleted_obj = l_incident.delete()
            return Response(deleted_obj, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)
