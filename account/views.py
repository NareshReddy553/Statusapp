import logging
from django.conf import settings

from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import Users
from account.password_serializer import PasswordChangeSerializer
from account.reset_password_serializer import ResetPasswordRequestSerializer, ResetPasswordSerializer

from .permissions import IsSecurityAdmin


logger = logging.getLogger("account.views")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    rst = {}
    rst["Profile"] = model_to_dict(Users.objects.get(pk=request.user.pk))
    rst["Privileges"] = request.user.privileges
    return Response(rst)


class ResetPasswordRequestView(APIView):
    """
    Api for forgot password request.
    """

    def post(self, request, *args, **kwargs):
        ser = ResetPasswordRequestSerializer(data=request.data)
        if ser.is_valid():
            ser.validated_data["user_profile"].send_reset_password_request_email()
        return Response(status=status.HTTP_202_ACCEPTED)

    def put(self, request, *args, **kwargs):
        ser = ResetPasswordSerializer(data=request.data)
        if ser.is_valid(raise_exception=True):
            ser.save()
        return Response(status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    APi for change password.
    """

    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        ser = PasswordChangeSerializer(
            data=request.data, context={"user": request.user}
        )
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(status=status.HTTP_200_OK)