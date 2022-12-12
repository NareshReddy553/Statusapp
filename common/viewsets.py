from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from common.models import Components, Incidents
from common.serializers import ComponentsSerializer, IncidentSerializer


class FilterBusinessUnitViewset(viewsets.ModelViewSet):
    def get_queryset(self):
        pass


class IncidentsViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = IncidentSerializer

    def get_queryset(self):
        l_businessunit = self.request.headers.get('businessunit')
        queryset = Incidents.objects.filter(
            businessunit__businessunit_name=l_businessunit, is_active=True)
        return queryset

    @action(detail=True, methods=["patch"], url_path="update_incident")
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

    @action(detail=True, methods=["patch"], url_path="update_incident")
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
