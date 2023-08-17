from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from account.utils import get_hashed_password

from .models import Users, UsersPassword


class PasswordField(serializers.CharField):
    def to_internal_value(self, password):
        validate_password(password)
        return password


class PasswordChangeSerializer(serializers.Serializer):
    password = PasswordField()
    user = serializers.PrimaryKeyRelatedField(
        queryset=Users.objects.all(), required=False, allow_null=True
    )

    def create(self, validated_data, *args, **kwargs):
        user = self.context["user"]
        if validated_data.get("user"):
            user = validated_data["user"]
        
        password_hash = get_hashed_password(validated_data["password"])
        UsersPassword.objects.create(
            user=user,
            password=password_hash,
        )
        return user
