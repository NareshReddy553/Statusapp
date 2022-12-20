from django.db import models


class Users(models.Model):

    user_id = models.AutoField(db_column='USER_ID', primary_key=True)

    email = models.CharField(db_column='EMAIL', max_length=100)

    first_name = models.CharField(
        db_column='FIRST_NAME', max_length=100, blank=True, null=True)

    last_name = models.CharField(
        db_column='LAST_NAME', max_length=100, blank=True, null=True)

    phone_number = models.IntegerField(
        db_column='PHONE_NUMBER', blank=True, null=True)

    is_active = models.BooleanField(db_column='IS_ACTIVE')

    lastlogin_date = models.DateTimeField(
        db_column='LASTLOGIN_DATE', blank=True, null=True)

    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME')

    modify_datetime = models.DateTimeField(db_column='MODIFY_DATETIME')
    last_businessiunit_name = models.CharField(
        db_column='LAST_BUSINESSIUNIT_NAME', max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class Priv(models.Model):

    priv_id = models.AutoField(db_column='PRIV_ID', primary_key=True)

    priv_name = models.CharField(db_column='PRIV_NAME', max_length=100)

    description = models.CharField(
        db_column='DESCRIPTION', max_length=300, blank=True, null=True)

    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME')

    modify_datetime = models.DateTimeField(db_column='MODIFY_DATETIME')

    class Meta:
        managed = False
        db_table = 'priv'


class Role(models.Model):

    role_id = models.AutoField(db_column='ROLE_ID', primary_key=True)

    role_name = models.CharField(db_column='ROLE_NAME', max_length=100)

    description = models.CharField(
        db_column='DESCRIPTION', max_length=300, blank=True, null=True)

    active = models.IntegerField(db_column='ACTIVE')

    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME')

    modify_datetime = models.DateTimeField(db_column='MODIFY_DATETIME')

    class Meta:
        managed = False
        db_table = 'role'


class RolesPrivs(models.Model):

    rolepriv_id = models.AutoField(db_column='ROLEPRIV_ID', primary_key=True)

    role = models.ForeignKey(
        Role, related_name="privs", on_delete=models.CASCADE
    )
    # role_id = models.IntegerField(db_column='ROLE_ID')

    priv = models.ForeignKey(
        Priv, related_name="privs_roles", on_delete=models.CASCADE
    )
    # priv_id = models.IntegerField(db_column='PRIV_ID')

    class Meta:
        managed = False
        db_table = 'roles_privs'


class UserRoles(models.Model):

    userrole_id = models.AutoField(db_column='USERROLE_ID', primary_key=True)

    user = models.ForeignKey(
        Users, related_name="roles", on_delete=models.CASCADE
    )
    # user_id = models.IntegerField(db_column='USER_ID')

    role = models.ForeignKey(
        Role, related_name="user_roles", on_delete=models.CASCADE
    )
    # role_id = models.IntegerField(db_column='ROLE_ID')

    class Meta:
        managed = False
        db_table = 'user_roles'


class UsersPassword(models.Model):

    userpassword_id = models.AutoField(
        db_column='USERPASSWORD_ID', primary_key=True)

    password = models.CharField(db_column='PASSWORD', max_length=300)

    password_datetime = models.DateTimeField(db_column='PASSWORD_DATETIME')

    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME')

    user = models.ForeignKey(
        Users, related_name="users", on_delete=models.CASCADE
    )
    # user_id = models.IntegerField(db_column='USER_ID')

    class Meta:
        managed = False
        db_table = 'users_password'
