
from django.conf import settings
from rest_framework import serializers
from django.db import transaction
from account.models import Users, UsersPassword
from account.utils import get_hashed_password
from account.validators import random_password_generate
from common.serializers import BusinessUnitSerializer


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = '__all__'
        
    
       
       


class UsersProfileSerializer(serializers.ModelSerializer):
    
    
    @transaction.atomic
    def create(self, validated_data):
        validated_data["email"] = validated_data.get("email", validated_data.get("username"))
        user=super().create(validated_data)
        password=random_password_generate()
        UsersPassword.objects.create(user=user, password=get_hashed_password(password))
        # send password to user mail 
        kargs={"password":password}
        user.send_new_user_request(password)
        return user
    class Meta:
        model = Users
        fields = '__all__'
