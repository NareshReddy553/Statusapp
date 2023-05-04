# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import base64
import hashlib
import uuid
from django.conf import settings
from django.db import IntegrityError, models

from account.account_models import Users
from account.utils import get_hashed_password
from common.softdelete.managers import SoftDeleteManger
from common.softdelete.models import SoftDeleteModelMixin
from common.softdelete.querysets import SoftDeletionQuerySet
from common.exceptions import DuplicateUsernameError

DUPLICATE_USERNAME_ERROR = "Duplicate Email Error"

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
    description = models.CharField(
        db_column='DESCRIPTION', max_length=12000, blank=True, null=True)
    is_active = models.BooleanField(db_column='IS_ACTIVE', default=True)
    is_group = models.BooleanField(db_column='IS_GROUP')
    group_no = models.IntegerField(db_column='GROUP_NO')
    display_order = models.IntegerField(db_column='DISPLAY_ORDER')
    subgroup_display_order = models.IntegerField(
        db_column='SUBGROUP_DISPLAY_ORDER')
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='component_bs')
    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME',auto_now_add=True)
    modified_datetime = models.DateTimeField(db_column='MODIFIED_DATETIME',auto_now=True)
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
    
    impact_severity = models.CharField(db_column='Impact Severity', max_length=100)  
    acer_number = models.IntegerField(db_column='ACER number')  
    start_time = models.DateTimeField(db_column='Start time', blank=True, null=True)  
    end_time = models.DateTimeField(db_column='End time', blank=True, null=True)  
    issue_impact = models.CharField(db_column='Issue Impact', max_length=250)

    class Meta:
        managed = False
        db_table = 'incidents'
        ordering = ['-modify_datetime']


class Subscribers(models.Model):
    subscriber_id = models.AutoField(
        db_column='SUBSCRIBER_ID', primary_key=True)
    first_name = models.CharField(db_column='FIRST_NAME', max_length=200,blank=True,null=True)
    last_name = models.CharField(
        db_column='LAST_NAME', max_length=200, blank=True, null=True)
    email = models.EmailField(db_column='EMAIL', unique=True, max_length=500,blank=True, null=True)
    phone_number = models.CharField(
        db_column='PHONE_NUMBER', unique=True, blank=True, null=True,max_length=10)
    is_active = models.BooleanField(db_column='IS_ACTIVE',default=True)
    email_delivery = models.BooleanField(
        db_column='EMAIL_DELIVERY', blank=True, null=True,default=False)
    sms_delivery = models.BooleanField(db_column='SMS_DELIVERY',default=False)
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='subscribers_bs')
    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME',auto_now_add=True)
    modify_datetime = models.DateTimeField(db_column='MODIFY_DATETIME',auto_now=True)
    subscriber_token=models.CharField(db_column='SUBSCRIBER_TOKEN',max_length=100,editable=False)

    class Meta:
        managed = False
        db_table = 'subscribers'
        ordering = ['-modify_datetime']
        
    def save(self, *args, **kwargs):
        try:
            super(Subscribers, self).save(*args, **kwargs)
        except IntegrityError as e:
            raise DuplicateUsernameError(
                "This Email is already exist.Please provide unique Email",
                DUPLICATE_USERNAME_ERROR,
                {"email": self.email},
            )


class IncidentComponent(models.Model):
    incident_component_id = models.AutoField(
        db_column='INCIDENT_COMPONENT_id', primary_key=True)
    # incident_id = models.IntegerField(db_column='INCIDENT_ID')
    incident = models.ForeignKey(
        Incidents, related_name="incidents_comp", on_delete=models.CASCADE)
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
    subscriber_component_id = models.AutoField(
        db_column='SUBSCRIBER_COMPONENT_ID', primary_key=True)
    # subcriber_id = models.IntegerField(db_column='SUBCRIBER_ID')
    subscriber = models.ForeignKey(
        Subscribers, related_name="compsubscribers", on_delete=models.CASCADE)
    # component_id = models.IntegerField(db_column='COMPONENT_ID')
    component = models.ForeignKey(
        Components, related_name="components", on_delete=models.CASCADE)
    is_active = models.BooleanField(db_column='IS_ACTIVE')
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='sub_com_bs')
    created_datetime = models.DateTimeField(db_column='CREATED_DATETIME',auto_now_add=True)
    modify_datetime = models.DateTimeField(db_column='MODIFY_DATETIME',auto_now=True)

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


class IncidentsActivity(models.Model):
    incidents_activity_id = models.AutoField(primary_key=True)
    # incident_id = models.IntegerField()
    incident = models.ForeignKey(
        Incidents, on_delete=models.CASCADE, related_name='inc_act')
    incident_name = models.CharField(max_length=250, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=25, blank=True, null=True)
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='inc_act_business')
    createduser_id = models.IntegerField(blank=True, null=True)
    modifieduser_id = models.IntegerField(blank=True, null=True)
    created_datetime = models.DateTimeField(
        blank=True, null=True, auto_now_add=True)
    modified_datetime = models.DateTimeField(
        blank=True, null=True, auto_now_add=True)
    
    impact_severity = models.CharField(db_column='Impact Severity', max_length=100)  
    acer_number = models.IntegerField(db_column='ACER number')  
    start_time = models.DateTimeField(db_column='Start time', blank=True, null=True)  
    end_time = models.DateTimeField(db_column='End time', blank=True, null=True)  
    issue_impact = models.CharField(db_column='Issue Impact', max_length=250)

    class Meta:
        managed = False
        db_table = 'incidents_activity'
        ordering=['-incident_id','-modified_datetime']


class IncidentsComponentActivitys(models.Model):
    incident_component_act_id = models.AutoField(primary_key=True)
    component_id = models.IntegerField(blank=True, null=True)
    createduser_id = models.IntegerField(blank=True, null=True)
    created_datetime = models.DateTimeField(blank=True, null=True)
    incidents_activity_id = models.IntegerField(blank=True, null=True)
    component_name = models.CharField(max_length=100, blank=True, null=True)
    component_status = models.CharField(max_length=100, blank=True, null=True)
    component_status_id = models.IntegerField(blank=True, null=True)
    incident_id=models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Incidents_component_activitys'
        
class Smsgateway(models.Model):
    network_id = models.AutoField(db_column='NETWORK_ID', primary_key=True)
    network = models.CharField(db_column='NETWORK', unique=True, max_length=100)
    pemail = models.CharField(db_column='PEMAIL', max_length=100)

    class Meta:
        managed = False
        db_table = 'smsgateway'
        


class ScheduledMaintenance(models.Model):
    sch_inc_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, blank=True, null=True)
    message = models.CharField(max_length=2000, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True,default=True)
    schstartdate = models.DateTimeField(db_column='schStartDate',blank=False,null=False) 
    schenddate = models.DateTimeField(db_column='schEndDate',blank=False,null=False) 
    is_done = models.BooleanField(blank=True, null=True,default=False)
    auto_complete = models.BooleanField(blank=True, null=True,default=False)
    created_datetime = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    modified_datetime = models.DateTimeField(blank=True, null=True,auto_now=True)
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='sch_mnt_business')
    status = models.CharField(max_length=100, blank=True, null=True,default='Scheduled')
    impact_update=models.CharField(max_length=1000)

    class Meta:
        managed = False
        db_table = 'Scheduled_Maintenance'
        ordering = ['-modified_datetime']

class SchMntComponent(models.Model):
    sch_mnt_com_id = models.AutoField(primary_key=True)
    sch_inc= models.ForeignKey(
        ScheduledMaintenance, on_delete=models.CASCADE, related_name='sch_mnt')
    component = models.ForeignKey(
        Components, related_name="sch_mnt_components", on_delete=models.CASCADE)
    is_active = models.BooleanField(blank=True, null=True,default=True)
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='sch_mnt_comp_bus+')
    created_datetime = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    modified_datetime = models.DateTimeField(blank=True, null=True,auto_now=True)

    class Meta:
        managed = False
        db_table = 'Sch_mnt_component'


class SchMntActivity(models.Model):
    sch_mnt_activity_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    message = models.CharField(max_length=100, blank=True, null=True)
    schstartdate = models.DateTimeField(db_column='schStartDate', blank=True, null=True) 
    schenddate = models.DateTimeField(db_column='schEndDate', blank=True, null=True)  
    createduser_id = models.IntegerField(blank=True, null=True)
    created_datetime = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    # sch_inc_id = models.IntegerField()
    sch_inc = models.ForeignKey(
        ScheduledMaintenance, on_delete=models.CASCADE, related_name='sch_mnt_inc+')
    impact_update=models.CharField(max_length=1000)

    class Meta:
        managed = False
        db_table = 'Sch_mnt_activity'
        ordering = ['-sch_inc_id','-created_datetime']


class IncidentTemplate(models.Model):
    template_id = models.AutoField(primary_key=True)
    template_name = models.CharField(unique=True, max_length=250)
    incident_title = models.CharField(max_length=250,blank=True, null=True)
    description = models.CharField(max_length=2000, blank=True, null=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)
    createduser = models.ForeignKey(
        Users,
        models.DO_NOTHING,
        related_name="inc_temp_created_user+",
        blank=True,
        null=True,
    )
    modifieduser = models.ForeignKey(
        Users,
        models.DO_NOTHING,
        related_name="inc_temp_mdf_user+",
        blank=True,
        null=True,
    )
    businessunit = models.ForeignKey(
        Businessunits, on_delete=models.CASCADE, related_name='inc_temp_bus+')
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'Incident_Template'



class IncidentAdditionalRecipients(models.Model):
    inc_recipient_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=100)
    is_active = models.IntegerField(blank=True, null=True)
    created_datetime = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    incident=models.ForeignKey(
        Incidents, on_delete=models.CASCADE, related_name='inc_recipient+')
    class Meta:
        managed = False
        db_table = 'Incident_additional_recipients'
        
class SchMntAdditionalRecipients(models.Model):
    sch_mnt_recipient_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=100)
    is_active = models.IntegerField(blank=True, null=True)
    created_datetime = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    sch_inc=models.ForeignKey(
        ScheduledMaintenance, on_delete=models.CASCADE, related_name='sch_recipient+')

    class Meta:
        managed = False
        db_table = 'sch_mnt_additional_recipients'
        
        
class CommonLookups(models.Model):
    lookup_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=100)
    sub_caterogy = models.CharField(max_length=100)
    looup_name = models.CharField(max_length=100)
    looup_value = models.CharField(max_length=100)
    display_text = models.CharField(max_length=250)
    businessunit_id = models.IntegerField()
    created_datetime = models.DateTimeField(blank=True, null=True)
    modified_datetime = models.DateTimeField(blank=True, null=True)
    createduser_id = models.IntegerField(blank=True, null=True)
    modifieduser_id = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'common_lookups'