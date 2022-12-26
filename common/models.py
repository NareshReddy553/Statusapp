# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

from account.account_models import Users
from common.softdelete.managers import SoftDeleteManger
from common.softdelete.models import SoftDeleteModelMixin
from common.softdelete.querysets import SoftDeletionQuerySet


class Businessunits(models.Model):
    businessunit_id = models.AutoField(
        db_column='BUSINESSUNIT_ID', primary_key=True)
    businessunit_name = models.CharField(
        db_column='BUSINESSUNIT_NAME', unique=True, max_length=200, null=False, blank=False)
    is_active = models.BooleanField(db_column='IS_ACTIVE', default=True)
    created_datetime = models.DateTimeField(
        db_column='CREATED_DATETIME', auto_now_add=True)
    modify_datetime = models.DateTimeField(
        db_column='MODIFIED_DATETIME', auto_now=True)
    # createduser_id = models.IntegerField(db_column='CREATEDUSER_ID')
    # modifieduser_id = models.IntegerField(db_column='MODIFIEDUSER_ID')
    createduser = models.ForeignKey(
        Users,
        models.DO_NOTHING,
        related_name="bus_unt_created_user+",
        blank=True,
        null=True,
    )
    modifieduser = models.ForeignKey(
        Users,
        models.DO_NOTHING,
        related_name="bus_unt_mdf_user+",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = 'businessunits'


class ComponentsStatus(models.Model):
    component_status_id = models.AutoField(
        db_column='COMPONENT_STATUS_ID', primary_key=True)
    component_status_name = models.CharField(
        db_column='COMPONENT_STATUS_NAME', max_length=100)
    component_status_description = models.CharField(
        db_column='COMPONENT_STATUS_DESCRIPTION', max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'components_status'


class Components(models.Model):
    component_id = models.AutoField(db_column='COMPONENT_ID', primary_key=True)
    component_name = models.CharField(
        db_column='COMPONENT_NAME', max_length=500)
    decscription = models.CharField(
        db_column='DECSCRIPTION', max_length=12000, blank=True, null=True)
    is_active = models.BooleanField(db_column='IS_ACTIVE', default=True)
    is_group = models.BooleanField(db_column='IS_GROUP')
    group_no = models.IntegerField(db_column='GROUP_NO')
    display_order = models.IntegerField(db_column='DISPLAY_ORDER')
    subgroup_display_order = models.IntegerField(
        db_column='SUBGROUP_DISPLAY_ORDER')
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='component_bs')
    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME')
    modified_datetime = models.DateTimeField(db_column='MODIFIED_DATETIME')
    # createduser_id = models.IntegerField(db_column='CREATEDUSER_ID')
    # modifieduser_id = models.IntegerField(db_column='MODIFIEDUSER_ID')
    createduser = models.ForeignKey(
        Users,
        models.DO_NOTHING,
        related_name="com_created_user+",
        blank=True,
        null=True,
    )
    modifieduser = models.ForeignKey(
        Users,
        models.DO_NOTHING,
        related_name="com_mdf_user+",
        blank=True,
        null=True,
    )
    component_status = models.ForeignKey(
        ComponentsStatus, on_delete=models.CASCADE, related_name='component_status+')
    has_subgroup = models.BooleanField(
        db_column='HAS_SUBGROUP', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'components'
        ordering = ['display_order', 'subgroup_display_order']


class Incidents(SoftDeleteModelMixin):
    objects = SoftDeleteManger()
    incident_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    status = models.CharField(max_length=50, blank=True, null=True)
    message = models.CharField(max_length=2000, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True, default=True)
    incident_postmortem = models.CharField(
        max_length=2000, blank=True, null=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    modify_datetime = models.DateTimeField(auto_now=True)
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='incident_bs+')
    # createduser_id = models.IntegerField(db_column='CREATEDUSER_ID')
    # modifieduser_id = models.IntegerField(db_column='MODIFIEDUSER_ID')
    createduser = models.ForeignKey(
        Users,
        models.DO_NOTHING,
        related_name="inc_created_user+",
        blank=True,
        null=True,
    )
    modifieduser = models.ForeignKey(
        Users,
        models.DO_NOTHING,
        related_name="inc_mdf_user+",
        blank=True,
        null=True,
    )
    isdeleted = models.BooleanField(
        db_column='ISDELETED', blank=True, null=True, default=False)

    class Meta:
        managed = False
        db_table = 'incidents'
        ordering = ['-modify_datetime']


class Subscribers(models.Model):
    subscriber_id = models.AutoField(
        db_column='SUBSCRIBER_ID', primary_key=True)
    first_name = models.CharField(db_column='FIRST_NAME', max_length=200)
    last_name = models.CharField(
        db_column='LAST_NAME', max_length=200, blank=True, null=True)
    email = models.CharField(db_column='EMAIL', unique=True, max_length=500)
    phone_number = models.BigIntegerField(
        db_column='PHONE_NUMBER', unique=True, blank=True, null=True)
    is_active = models.BooleanField(db_column='IS_ACTIVE')
    email_delivery = models.IntegerField(
        db_column='EMAIL_DELIVERY', blank=True, null=True)
    sms_delivery = models.IntegerField(db_column='SMS_DELIVERY')
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='subscribers_bs')
    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME')
    modify_datetime = models.DateTimeField(db_column='MODIFY_DATETIME')

    class Meta:
        managed = False
        db_table = 'subscribers'


class IncidentComponent(models.Model):
    incident_component_id = models.AutoField(
        db_column='INCIDENT_COMPONENT_id', primary_key=True)
    # incident_id = models.IntegerField(db_column='INCIDENT_ID')
    incident = models.ForeignKey(
        Incidents, related_name="incidents", on_delete=models.CASCADE)
    # component_id = models.IntegerField(db_column='COMPONENT_ID')
    component = models.ForeignKey(
        Components, related_name="com", on_delete=models.CASCADE)
    is_active = models.BooleanField(db_column='IS_ACTIVE')
    created_datetime = models.DateTimeField(
        db_column='CREATED_DATETIME', auto_now_add=True)
    modify_datetime = models.DateTimeField(
        db_column='MODIFY_DATETIME', auto_now=True)
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='inc_com_bs')

    class Meta:
        managed = False
        db_table = 'incident_component'


class SubcriberComponent(models.Model):
    subcriber_component_id = models.AutoField(
        db_column='SUBCRIBER_COMPONENT_ID', primary_key=True)
    # subcriber_id = models.IntegerField(db_column='SUBCRIBER_ID')
    subscriber = models.ForeignKey(
        Subscribers, related_name="subscribers", on_delete=models.CASCADE)
    # component_id = models.IntegerField(db_column='COMPONENT_ID')
    component = models.ForeignKey(
        Components, related_name="components", on_delete=models.CASCADE)
    is_active = models.BooleanField(db_column='IS_ACTIVE')
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='sub_com_bs')
    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME')
    modify_datetime = models.DateTimeField(db_column='MODIFY_DATETIME')

    class Meta:
        managed = False
        db_table = 'subcriber_component'


class UserBusinessunits(models.Model):
    user_businessunits_id = models.AutoField(
        db_column='USER_BUSINESSUNITS_ID', primary_key=True)
    # user_id = models.IntegerField(db_column='USER_ID', blank=True, null=True)
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='usr_bs')
    # businessunit_id = models.IntegerField(
    #     db_column='BUSINESSUNIT_ID', blank=True, null=True)
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='bs_usr')
    allow_access = models.BooleanField(
        db_column='ALLOW_ACCESS', blank=True, null=True)
    created_datetime = models.DateTimeField(
        db_column='CREATED_DATETIME', blank=True, null=True)
    modified_datetime = models.DateTimeField(
        db_column='MODIFIED_DATETIME', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_businessunits'


class Sidebar(models.Model):
    sidebar_id = models.AutoField(db_column='SIDEBAR_ID', primary_key=True)
    sidebar_name = models.CharField(db_column='SIDEBAR_NAME', max_length=100)
    # businessunit_id = models.IntegerField(db_column='BUSINESSUNIT_ID')
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='sidebar_bs')

    createduser = models.ForeignKey(
        Users,
        models.DO_NOTHING,
        related_name="sbr_created_user+",
        blank=True,
        null=True,
    )
    modifieduser = models.ForeignKey(
        Users,
        models.DO_NOTHING,
        related_name="sbr_mdf_user+",
        blank=True,
        null=True,
    )
    created_datetime = models.DateTimeField(
        db_column='CREATED_DATETIME', blank=True, null=True)
    modified_datetime = models.DateTimeField(
        db_column='MODIFIED_DATETIME', blank=True, null=True)
    is_active = models.BooleanField(db_column='IS_ACTIVE')

    class Meta:
        managed = False
        db_table = 'sidebar'
