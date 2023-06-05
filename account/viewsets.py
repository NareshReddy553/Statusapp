import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from account.serializers import UsersProfileSerializer
from account.account_models import Users

from common.models import Components, Incidents
from common.serializers import ComponentsSerializer, IncidentSerializer


class UsersViewset(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    serializer_class = UsersProfileSerializer
    queryset = Users.objects.filter(is_active=True)
    pagination_class=None

    @action(detail=True, methods=["patch"], url_path="update_lastlogin")
    def update_userlast_businessunit(self, request, pk=None):
        input_data = request.data
        l_incident = self.get_object()
        l_incident.modify_datetime = datetime.datetime.now()
        serializer = self.serializer_class(
            l_incident, input_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
