import logging
from django.conf import settings

from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.account_models import Users

from .permissions import IsSecurityAdmin


logger = logging.getLogger("account.views")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    rst = {}
    rst["Profile"] = model_to_dict(Users.objects.get(pk=request.user.pk))
    rst["Privileges"] = request.user.privileges
    return Response(rst)
