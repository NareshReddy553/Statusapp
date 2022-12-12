from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from account.serializers import UsersProfileSerializer

from common.models import Components, Incidents
from common.serializers import ComponentsSerializer, IncidentSerializer


class UsersViewset(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    serializer_class = UsersProfileSerializer

    def get_queryset(self):
        return self.request.user
