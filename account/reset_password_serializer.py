from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from account.models import Users
from account.password_reset_model import PasswordResets

from .password_serializer import PasswordChangeSerializer


class ResetPasswordSerializer(PasswordChangeSerializer):
    # username = serializers.EmailField(write_only=True)
    token = serializers.UUIDField(write_only=True)

    def validate_token(self, token):
        password_reset = PasswordResets.objects.filter(
            token=token,
        ).last()
        if (
            not password_reset or password_reset.expire_datetime < timezone.now().date()
        ):  # or password_reset.email.lower() != data['username'].lower() :
            raise ValidationError("Invalid reset password request.")
        self.context["user"] = password_reset.user
        return token


class ResetPasswordRequestSerializer(serializers.Serializer):
    username = serializers.EmailField()

    def validate(self, data):
        user_profile = Users.objects.filter(email__iexact=data["username"]).last()
        if user_profile:
            data["user_profile"] = user_profile
        else:
            raise ValidationError({"username": "Username does not exists"})
        return data
