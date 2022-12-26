import datetime
from django.forms import ValidationError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from common.models import Components, IncidentComponent, Incidents
from common.serializers import ComponentsSerializer, IncidentSerializer


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
        l_incident = self.get_object()
        serializer = self.serializer_class(
            l_incident, input_data, partial=True)
        if serializer.is_valid():
            serializer.save()
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
