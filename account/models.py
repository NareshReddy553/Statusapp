import datetime
from django.db import models
from django.contrib.auth.password_validation import get_default_password_validators
from uuid import uuid4
from django.conf import settings
from django.utils import timezone

from account.tasks import send_email_notifications
from common.mailer import send_email, send_mass_mail


class Users(models.Model):

    user_id = models.AutoField(db_column="USER_ID", primary_key=True)
    email = models.CharField(db_column="EMAIL", max_length=100, unique=True)
    first_name = models.CharField(db_column="FIRST_NAME", max_length=100,)
    last_name = models.CharField(db_column="LAST_NAME", max_length=100, blank=True, null=True)
    phone_number = models.CharField(db_column="PHONE_NUMBER", max_length=10,blank=True, null=True)
    is_active = models.BooleanField(db_column="IS_ACTIVE",default=True)
    lastlogin_date = models.DateTimeField(db_column="LASTLOGIN_DATE", blank=True, null=True,auto_now=True)
    created_datetime = models.DateTimeField(db_column="CREATED_DATETIME", auto_now_add=True)
    modify_datetime = models.DateTimeField(db_column="MODIFY_DATETIME", auto_now=True)
    last_businessiunit_name = models.CharField(db_column="LAST_BUSINESSIUNIT_NAME", max_length=200, blank=True, null=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def send_reset_password_request_email(self):
        from .password_reset_model import PasswordResets

        token = uuid4()
        now = timezone.now()
        password_reset_obj = PasswordResets.objects.create(
            user=self,
            email=self.email,
            token=token,
            expire_datetime=now
            + datetime.timedelta(minutes=settings.PASSWORD_RESET_TIMEOUT_MINUTES),
        )
        context = {
            "full_name": self.full_name,
            "email": self.email,
            "expiry_minutes": settings.PASSWORD_RESET_TIMEOUT_MINUTES,
            "FORGOT_PASSWORD_URL": settings.FORGOT_PASSWORD_URL,
            "token": token,
        }
        msg=send_email(
            template="reset-password-request.html",
            subject="Forgotten Password",
            context_data=context,
            recipient_list=['naresh.gangireddy@data-axle.com',"manasa.gangumolu@data-axle.com"],
        )
        send_mass_mail([msg])
    
    def send_new_user_request(self,password):
        email_send_list=[]
        subject="new user request"
        context = {
            "full_name": self.full_name,
            "email": self.email,
            "password":password,
            "expiry_minutes": settings.PASSWORD_RESET_TIMEOUT_MINUTES,
            "LOGIN_URL": settings.LOGIN_URL
        }
        # email_send_list.append({
        #                 "subject":subject,
        #                 "context":context,
        #                 "recipients":[self.email]
        #             })
        # if email_send_list:
        #     send_email_notifications.delay('new_user_password_notification.html',email_send_list)
        msg=send_email("new_user_password_notification.html", context, subject, ['naresh.gangireddy@data-axle.com',"manasa.gangumolu@data-axle.com"])
        send_mass_mail([msg])
        
    class Meta:
        managed = False
        db_table = "users"


class Priv(models.Model):

    priv_id = models.AutoField(db_column="PRIV_ID", primary_key=True)

    priv_name = models.CharField(db_column="PRIV_NAME", max_length=100)

    description = models.CharField(
        db_column="DESCRIPTION", max_length=300, blank=True, null=True
    )

    created_datetime = models.DateTimeField(db_column="CREATED_DATETIME")

    modify_datetime = models.DateTimeField(db_column="MODIFY_DATETIME")

    class Meta:
        managed = False
        db_table = "priv"


class Role(models.Model):

    role_id = models.AutoField(db_column="ROLE_ID", primary_key=True)

    role_name = models.CharField(db_column="ROLE_NAME", max_length=100)

    description = models.CharField(
        db_column="DESCRIPTION", max_length=300, blank=True, null=True
    )

    active = models.IntegerField(db_column="ACTIVE")

    created_datetime = models.DateTimeField(db_column="CREATED_DATETIME")

    modify_datetime = models.DateTimeField(db_column="MODIFY_DATETIME")

    class Meta:
        managed = False
        db_table = "role"


class RolesPrivs(models.Model):

    rolepriv_id = models.AutoField(db_column="ROLEPRIV_ID", primary_key=True)

    role = models.ForeignKey(Role, related_name="privs", on_delete=models.CASCADE)
    # role_id = models.IntegerField(db_column='ROLE_ID')

    priv = models.ForeignKey(Priv, related_name="privs_roles", on_delete=models.CASCADE)
    # priv_id = models.IntegerField(db_column='PRIV_ID')

    class Meta:
        managed = False
        db_table = "roles_privs"


class UserRoles(models.Model):

    userrole_id = models.AutoField(db_column="USERROLE_ID", primary_key=True)

    user = models.ForeignKey(Users, related_name="roles", on_delete=models.CASCADE)
    # user_id = models.IntegerField(db_column='USER_ID')

    role = models.ForeignKey(Role, related_name="user_roles", on_delete=models.CASCADE)
    # role_id = models.IntegerField(db_column='ROLE_ID')

    class Meta:
        managed = False
        db_table = "user_roles"


class UsersPassword(models.Model):

    userpassword_id = models.AutoField(db_column="USERPASSWORD_ID", primary_key=True)
    password = models.CharField(
        max_length=128,
        validators=[v.validate for v in get_default_password_validators()],
    )
    password_datetime = models.DateTimeField(db_column="PASSWORD_DATETIME",auto_now_add=True)
    created_datetime = models.DateTimeField(db_column="CREATED_DATETIME",auto_now_add=True)
    user = models.ForeignKey(Users, related_name="users", on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "users_password"

