from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from account.models import Users
from account.permissions import IsSystemAdmin
from common.serializers import BusinessUnitSerializer
from rest_framework import status


class UsersBusinessUnitView(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    permission_classes = (permissions.IsAuthenticated,
                          IsSystemAdmin)
    serializer_class = BusinessUnitSerializer()

    def post(self, request, format=None):
        """
        It will create a new business unit.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        businessunit = serializer.save()

        return Response(status=status.HTTP_201_CREATED)

        l_user = request.user
        input_data = request.data

        # return Response(usernames)
