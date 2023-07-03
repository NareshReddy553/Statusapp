
from rest_framework import serializers

from account.account_models import Users
from common.serializers import BusinessUnitSerializer


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = '__all__'


class UsersProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = '__all__'
