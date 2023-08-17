from django.db import models
from account.models import Users


class PasswordResets(models.Model):
    passwordreset_id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(
        Users, models.DO_NOTHING, related_name="password_resets"
    )
    email = models.CharField(max_length=128)
    token = models.CharField(max_length=64)
    expire_datetime = models.DateField()

    class Meta:
        managed = False
        db_table = "PASSWORD_RESETS"
