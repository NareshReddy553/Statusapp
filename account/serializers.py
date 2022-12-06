
from rest_framework import serializer

from account.models import Users


class UsersSerializer(serializer.ModelSerializer):

    class Meta:
        model = Users
        fields = '__all__'
