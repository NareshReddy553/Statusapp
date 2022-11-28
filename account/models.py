from django.db import models


class Users(models.Model):
    # Field name made lowercase.
    user_id = models.AutoField(db_column='USER_ID', primary_key=True)
    # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=100)
    # Field name made lowercase.
    first_name = models.CharField(
        db_column='FIRST_NAME', max_length=100, blank=True, null=True)
    # Field name made lowercase.
    last_name = models.CharField(
        db_column='LAST_NAME', max_length=100, blank=True, null=True)
    # Field name made lowercase.
    phone_number = models.IntegerField(
        db_column='PHONE_NUMBER', blank=True, null=True)
    # Field name made lowercase.
    is_active = models.IntegerField(db_column='IS_ACTIVE')
    # Field name made lowercase.
    lastlogin_date = models.DateTimeField(
        db_column='LASTLOGIN_DATE', blank=True, null=True)
    # Field name made lowercase.
    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME')
    # Field name made lowercase.
    modify_datetime = models.DateTimeField(db_column='MODIFY_DATETIME')

    class Meta:
        managed = False
        db_table = 'users'


class Priv(models.Model):
    # Field name made lowercase.
    priv_id = models.AutoField(db_column='PRIV_ID', primary_key=True)
    # Field name made lowercase.
    priv_name = models.CharField(db_column='PRIV_NAME', max_length=100)
    # Field name made lowercase.
    description = models.CharField(
        db_column='DESCRIPTION', max_length=300, blank=True, null=True)
    # Field name made lowercase.
    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME')
    # Field name made lowercase.
    modify_datetime = models.DateTimeField(db_column='MODIFY_DATETIME')

    class Meta:
        managed = False
        db_table = 'priv'


class Role(models.Model):
    # Field name made lowercase.
    role_id = models.AutoField(db_column='ROLE_ID', primary_key=True)
    # Field name made lowercase.
    role_name = models.CharField(db_column='ROLE_NAME', max_length=100)
    # Field name made lowercase.
    description = models.CharField(
        db_column='DESCRIPTION', max_length=300, blank=True, null=True)
    # Field name made lowercase.
    active = models.IntegerField(db_column='ACTIVE')
    # Field name made lowercase.
    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME')
    # Field name made lowercase.
    modify_datetime = models.DateTimeField(db_column='MODIFY_DATETIME')

    class Meta:
        managed = False
        db_table = 'role'


class RolesPrivs(models.Model):
    # Field name made lowercase.
    rolepriv_id = models.AutoField(db_column='ROLEPRIV_ID', primary_key=True)
    # Field name made lowercase.
    role = models.ForeignKey(
        Role, related_name="privs", on_delete=models.CASCADE
    )
    # role_id = models.IntegerField(db_column='ROLE_ID')
    # Field name made lowercase.
    priv = models.ForeignKey(
        Priv, related_name="privs_roles", on_delete=models.CASCADE
    )
    # priv_id = models.IntegerField(db_column='PRIV_ID')

    class Meta:
        managed = False
        db_table = 'roles_privs'


class UserRoles(models.Model):
    # Field name made lowercase.
    userrole_id = models.AutoField(db_column='USERROLE_ID', primary_key=True)
    # Field name made lowercase.
    user = models.ForeignKey(
        Users, related_name="roles", on_delete=models.CASCADE
    )
    # user_id = models.IntegerField(db_column='USER_ID')
    # Field name made lowercase.
    role = models.ForeignKey(
        Role, related_name="user_roles", on_delete=models.CASCADE
    )
    # role_id = models.IntegerField(db_column='ROLE_ID')

    class Meta:
        managed = False
        db_table = 'user_roles'


class UsersPassword(models.Model):
    # Field name made lowercase.
    userpassword_id = models.AutoField(
        db_column='USERPASSWORD_ID', primary_key=True)
    # Field name made lowercase.
    password = models.CharField(db_column='PASSWORD', max_length=300)
    # Field name made lowercase.
    password_datetime = models.DateTimeField(db_column='PASSWORD_DATETIME')
    # Field name made lowercase.
    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME')
    # Field name made lowercase.
    user = models.ForeignKey(
        Users, related_name="users", on_delete=models.CASCADE
    )
    # user_id = models.IntegerField(db_column='USER_ID')

    class Meta:
        managed = False
        db_table = 'users_password'
