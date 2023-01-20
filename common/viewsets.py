import datetime
from django.forms import ValidationError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from common.models import Businessunits, Components, IncidentComponent, Incidents, IncidentsActivity
from common.serializers import ComponentsSerializer, IncidentSerializer, IncidentsActivitySerializer
from common.utils import get_component_status
from common.mailer import send_email


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
            incident_id=input_data.get('incident_id'))
        serializer = self.serializer_class(l_queryset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
