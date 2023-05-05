from datetime import datetime
from rest_framework import serializers, status
from rest_framework.response import Response
from account.services import get_cached_user
from django.db import transaction
from django.db.models import Q
from account.utils import get_hashed_password, get_subscriber_hashed
from django.utils.translation import gettext_lazy as _

from common.models import Businessunits, Components, ComponentsStatus, IncidentAdditionalRecipients, IncidentComponent, IncidentTemplate, Incidents, IncidentsComponentActivitys, SchMntAdditionalRecipients, SchMntComponent, ScheduledMaintenance, Smsgateway, SubcriberComponent, IncidentsActivity, Subscribers,SchMntActivity
from common.mailer import send_email, send_mass_mail
from rest_framework.exceptions import ValidationError
import logging


logger=logging.getLogger("common.serializers")


class BusinessUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Businessunits
        fields = '__all__'


class ComponentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentsStatus
        fields = '__all__'


class ComponentsSerializer(serializers.ModelSerializer):
    component_status = ComponentStatusSerializer()
    businessunit = BusinessUnitSerializer()

    class Meta:
        model = Components
        fields = '__all__'

class IncidentAdditionalRecipientsSerializer(serializers.ModelSerializer):
    # createduser = serializers.SerializerMethodField()
    # def get_createduser(self, obj):
    #     return get_cached_user(obj.createduser_id)
    
    class Meta:
        model = IncidentAdditionalRecipients
        fields = '__all__'
        
class SchMntAdditionalRecipientsSerializer(serializers.ModelSerializer):
    # createduser = serializers.SerializerMethodField()
    # def get_createduser(self, obj):
    #     return get_cached_user(obj.createduser_id)
    
    
    class Meta:
        model = SchMntAdditionalRecipients
        fields = '__all__'


class IncidentsComponentsSerializer(serializers.ModelSerializer):
    Components = ComponentsSerializer(many=True, read_only=True)

    class Meta:
        model = IncidentComponent
        fields = '__all__'


class IncidentSerializer(serializers.ModelSerializer):
    businessunit = BusinessUnitSerializer(required=False)
    createduser = serializers.SerializerMethodField()
    modifieduser = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField('get_incident_id')
    components = serializers.SerializerMethodField()
    recipients=serializers.SerializerMethodField()
    
    
    def get_recipients(self, obj):
        recipient_obj=IncidentAdditionalRecipients.objects.filter(incident=obj,is_active=True)
        serializer=IncidentAdditionalRecipientsSerializer(recipient_obj,many=True)
        return serializer.data

    def get_createduser(self, obj):
        return get_cached_user(obj.createduser_id)

    def get_modifieduser(self, obj):
        return get_cached_user(obj.modifieduser_id)

    def get_incident_id(self, obj):
        return obj.incident_id

    def get_components(self, obj):
        final_list = []
        inc_comp_obj = IncidentComponent.objects.filter(
            incident=obj.pk, is_active=True)
        if inc_comp_obj:
            for data_obj in inc_comp_obj:
                temp_dict = {}
                l_last_component_status=None
                if obj.status=='resolved':
                    l_last_component_status=IncidentsComponentActivitys.objects.filter(incident_id=obj.pk,component_id=data_obj.component.component_id).order_by('-created_datetime')
                if data_obj.component.is_active:
                    temp_dict['component_id'] = data_obj.component.component_id
                    temp_dict['component_name'] = data_obj.component.component_name
                    temp_dict['component_status'] = data_obj.component.component_status.component_status_name
                    if l_last_component_status and len(l_last_component_status) >= 2:
                        temp_dict['last_component_status'] = l_last_component_status[1].component_status
                    else:
                        temp_dict['last_component_status'] = None
                    temp_dict['businessunit'] = data_obj.component.businessunit.businessunit_name
                    final_list.append(temp_dict)
        return final_list

    class Meta:
        model = Incidents
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        l_businessunit_name = self.context['request'].headers.get(
            'businessunit')
        user = self.context['request'].user
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True).first()
        validated_data['businessunit'] = businessunit_qs
        validated_data['createduser'] = user
        validated_data['modifieduser'] = user
        l_incident = super().create(validated_data)
        components_list = self.initial_data.get('components', None)
        components_effected = list()
        l_incident_components_activity = list()
        Subscriber_list = list()
        if not components_list :
            raise ValidationError({"Error":"Please select atleast one component"})
            # Need entry in the incident component table which incident_id and component_id with respect to business_id
        l_inc_com_obj = [IncidentComponent(
            incident_id=l_incident.pk,
            component_id=cmp_sts.get('component_id'),
            is_active=True,
            businessunit=businessunit_qs
        ) for cmp_sts in components_list]
        
        for cmp_sts in components_list:
            component_status_obj = ComponentsStatus.objects.filter(
                component_status_name=cmp_sts.get('component_status')).first()
            # update the component status in component table
            update_component_obj = Components.objects.filter(pk=cmp_sts.get('component_id')).first()
            update_component_obj.component_status = component_status_obj
            update_component_obj.modified_datetime=datetime.now()
            update_component_obj.modifieduser=user
            update_component_obj.save()
            components_effected.append(update_component_obj.component_name)
            # We have to get the component subscribers from incident created

            subcomp_obj = list(SubcriberComponent.objects.filter(
                component_id=cmp_sts.get('component_id'), businessunit=businessunit_qs, is_active=True).values_list('subscriber__subscriber_id', flat=True))
            if subcomp_obj:
                Subscriber_list += (subcomp_obj)

        inc_cmp_obj = IncidentComponent.objects.bulk_create(l_inc_com_obj)

        l_incident_activity=IncidentsActivity.objects.create(
                    incident_id=l_incident.pk,
                    incident_name=l_incident.name,
                    message=l_incident.message,
                    status=l_incident.status,
                    businessunit_id=l_incident.businessunit_id,
                    createduser_id=user.user_id,
                    modifieduser_id=user.user_id,
                    created_datetime=datetime.now(),
                    modified_datetime=datetime.now(),
                    impact_severity=l_incident.impact_severity,
                    acer_number=l_incident.acer_number,
                    start_time=l_incident.start_time,
                    end_time=l_incident.end_time,
                    issue_impact=l_incident.issue_impact)
        
        if l_incident_activity:
            
        # Need entry in the incident activity table each time when we create the incident
            if inc_cmp_obj:
                for inc_cmp_data in inc_cmp_obj:
                    cmp_qs = Components.objects.filter(
                        component_id=inc_cmp_data.component_id).first()
                    l_incident_components_activity.append(IncidentsComponentActivitys(
                        incidents_activity_id=l_incident_activity.pk,
                        component_id=cmp_qs.component_id,
                        component_name=cmp_qs.component_name,
                        component_status=cmp_qs.component_status.component_status_name,
                        component_status_id=cmp_qs.component_status.component_status_id,
                        createduser_id=user.user_id,
                        created_datetime=datetime.now(),
                        incident_id=l_incident.pk))
        recipients = self.initial_data.get('recipients', [])
        create_recipients=[]
        if recipients:
            for mail in recipients:
                create_recipients.append(IncidentAdditionalRecipients(email=mail,is_active=True,incident=l_incident))
                
        if create_recipients:
            IncidentAdditionalRecipients.objects.bulk_create(create_recipients)
            
        if l_incident_components_activity:
            incident_activity_obj = IncidentsComponentActivitys.objects.bulk_create(
                l_incident_components_activity)
        
        if Subscriber_list:
                
            l_mass_email=[]
            subscribers_email = list(Subscribers.objects.filter(
                subscriber_id__in=Subscriber_list).values_list('email','subscriber_token'))
            l_status = str(l_incident.status).capitalize()
            context = {
                "incident_data": l_incident,
                "component_data": components_effected,
                "user": user.email,
                "businessunit":l_businessunit_name,
                "status":l_status
            }
            # x = datetime.now().strftime("%x %I:%M %p")
            l_status = str(l_incident.status).capitalize()
            subject = f"[{l_businessunit_name} platform status updates] Incident {l_status} - Admin"
            
            l_mass_email.append(send_email(
                template="incident_email_notification.html",
                subject=subject,
                context_data=context,
                recipient_list=[user.email]+recipients
            ))
            
            for email,token in subscribers_email:
                context["unsubscribe_url"]="http://18.118.80.163/Status/"+l_businessunit_name+'/unsubscribe/'+token
                l_mass_email.append(send_email(
                    template="incident_email_notification.html",
                    subject=subject,
                    context_data=context,
                    recipient_list=[email]
                ))
            
            send_mass_mail(l_mass_email)
        
        return l_incident


class IncidentsActivitySerializer(serializers.ModelSerializer):
    businessunit = BusinessUnitSerializer(required=False)
    createduser = serializers.SerializerMethodField()
    modifieduser = serializers.SerializerMethodField()
    components = serializers.SerializerMethodField()

    def get_components(self, obj):
        serializer = IncidentsComponentActivitysSerializer(IncidentsComponentActivitys.objects.filter(incidents_activity_id=obj.pk), many=True)
        return serializer.data
    
    def get_createduser(self, obj):
        return get_cached_user(obj.createduser_id)

    def get_modifieduser(self, obj):
        return get_cached_user(obj.modifieduser_id)
    class Meta:
        model = IncidentsActivity
        fields = '__all__'
class StatusPageIncidentsActivitySerializer(serializers.ModelSerializer):
    components = serializers.SerializerMethodField()

    def get_components(self, obj):
        serializer = IncidentsComponentActivitysSerializer(IncidentsComponentActivitys.objects.filter(incidents_activity_id=obj.pk), many=True)
        return serializer.data
    
    class Meta:
        model = IncidentsActivity
        fields = '__all__'
        
class StatusPageIncidentsSerializer(serializers.ModelSerializer):
    activity_history=serializers.SerializerMethodField()
    def get_activity_history(self,obj):
        serializer = StatusPageIncidentsActivitySerializer(IncidentsActivity.objects.filter(incident=obj), many=True)
        return serializer.data
        
    class Meta:
        model = Incidents
        fields = '__all__'
class IncidentsComponentActivitysSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = IncidentsComponentActivitys
        fields = '__all__'

class SubscribersSerializer(serializers.ModelSerializer):
    businessunit = BusinessUnitSerializer(required=False)
    components=serializers.SerializerMethodField()
    
    def get_components(self,obj):
        component_obj=Components.objects.filter(component_id__in=SubcriberComponent.objects.filter(subscriber_id=obj.subscriber_id,businessunit=obj.businessunit,is_active=True).values_list('component_id',flat=True))
        serializer=ComponentsSerializer(component_obj,many=True)
        return serializer.data
    class Meta:
        model = Subscribers
        fields = '__all__'
        
        
    @transaction.atomic
    def create(self, validated_data):
        l_businessunit_name = self.context['businessunit']
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True).first()
        validated_data['businessunit'] = businessunit_qs
        components_list = self.initial_data.get('components', None)
        if not components_list:
            raise ValidationError({"Error":"Please select atleast one component"})
        
        if self.initial_data.get('email_delivery', None):
            validated_data['email_delivery']=True
            
        elif self.initial_data.get('sms_delivery', None):
            l_network=self.initial_data.get('network', None)
            if l_network:
                l_network_mail=Smsgateway.objects.get(network=l_network).pemail
                if l_network_mail:
                    validated_data['email']=validated_data['phone_number']+"@"+l_network_mail
                    validated_data['sms_delivery']=True
                    
        else:
            raise ValidationError("subscriber type is required in payload")
        hashed_key=get_subscriber_hashed(validated_data['email'])
        validated_data['subscriber_token']=hashed_key[:20]
        instance = super().create(validated_data)
         
        # Need entry in the subscriber component table which subscriber_id and component_id with respect to business_id
        l_sub_com_obj = [SubcriberComponent(
            subscriber_id=instance.pk,
            component_id=cmp_sts,
            is_active=True,
            businessunit=businessunit_qs
        ) for cmp_sts in components_list]
        if l_sub_com_obj:
           inc_cmp_obj = SubcriberComponent.objects.bulk_create(l_sub_com_obj) 
        #    Need to send the conformation mail
        subscriber_Hash_id=instance.subscriber_token
        subscribers_email=[instance.email]
        businessunit_name=l_businessunit_name
        if subscribers_email:
            l_mass_email=[]
            context = {
                "subscriber": instance,
                "businessunit":l_businessunit_name,
                "subscriber_Hash_id":subscriber_Hash_id,
                "manage_subscriber_url":"http://18.118.80.163/Status/"+l_businessunit_name+'/manage/'+subscriber_Hash_id,
                "unsubscribe_url":"http://18.118.80.163/Status/"+l_businessunit_name+'/unsubscribe/'+subscriber_Hash_id
                
            }
            x = datetime.now().strftime("%x %I:%M %p")
            subject = f"[{businessunit_name} platform status updates] Welcome to {businessunit_name} platform status application"
            logger.info("sending notification to subscribers ")
            l_mass_email.append(send_email(
                template="subscriber_email_notification.html",
                subject=subject,
                context_data=context,
                recipient_list=subscribers_email,
            ))
            
            send_mass_mail(l_mass_email)
            
        return instance
    
    
class ScheduledMaintanenceSerializer(serializers.ModelSerializer):
    businessunit = BusinessUnitSerializer(required=False)
    components = serializers.SerializerMethodField()
    recipients=serializers.SerializerMethodField()
    schstartdate=serializers.DateTimeField(error_messages = {
        'invalid': _('This field is required')
    })
    schenddate=serializers.DateTimeField(error_messages = {
        'invalid': _('This field is required')
    })
    
    def get_components(self, obj):
        component_obj=Components.objects.filter(component_id__in=SchMntComponent.objects.filter(sch_inc=obj,businessunit=obj.businessunit,is_active=True).values_list('component_id',flat=True))
        serializer=ComponentsSerializer(component_obj,many=True)
        return serializer.data
    def get_recipients(self, obj):
        recipient_obj=SchMntAdditionalRecipients.objects.filter(sch_inc=obj,is_active=True)
        serializer=SchMntAdditionalRecipientsSerializer(recipient_obj,many=True)
        return serializer.data
    class Meta:
        model = ScheduledMaintenance
        fields = '__all__'
        
    
    @transaction.atomic
    def create(self, validated_data):
        l_businessunit_name = self.context['request'].headers.get(
            'businessunit')
        user = self.context['request'].user
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True).first()
        validated_data['businessunit'] = businessunit_qs
        # validated_data['createduser'] = user
        # validated_data['modifieduser'] = user
        components_list = self.initial_data.get('components', None)
        if not components_list:
            raise ValidationError({"Error":"Please select atleast one component"})
        l_sch_mnt = super().create(validated_data)
        components_effected=[]
        Subscriber_list = list()
        if components_list is not None:
            # Need entry in the sheduled maintanence component table which scd_mnt_id and component_id with respect to business_id
            l_sch_mnt_com_obj = [SchMntComponent(
                sch_inc=l_sch_mnt,
                component_id=cmp_sts.get('component_id'),
                is_active=True,
                businessunit=businessunit_qs
            ) for cmp_sts in components_list]
            for cmp_sts in components_list:
                # We have to get the component subscribers from incident created
                subcomp_obj = list(SubcriberComponent.objects.filter(
                    component_id=cmp_sts.get('component_id'), businessunit=businessunit_qs, is_active=True).values_list('subscriber__subscriber_id', flat=True))
                if subcomp_obj:
                    Subscriber_list += (subcomp_obj)
                component_obj=Components.objects.filter(component_id=cmp_sts.get('component_id')).first()
                components_effected.append(component_obj.component_name)
                # need to get list of component names that are effected
                

            sch_mnt_inc_cmp_obj = SchMntComponent.objects.bulk_create(l_sch_mnt_com_obj)
            # Need entry in the scheduled maintenance activity table each time when we create the scheduled maintenance incident
            if sch_mnt_inc_cmp_obj:
                SchMntActivity.objects.create(
                    sch_inc_id=l_sch_mnt.pk,
                    name=l_sch_mnt.name,
                    status=l_sch_mnt.status,
                    message=l_sch_mnt.message,
                    schstartdate=l_sch_mnt.schstartdate,
                    schenddate=l_sch_mnt.schenddate,
                    createduser_id=user.pk
                )
            # Adding additional recipients
            recipients = self.initial_data.get('recipients', [])
            create_recipients=[]
            if recipients:
                for mail in recipients:
                    create_recipients.append(SchMntAdditionalRecipients(email=mail,is_active=True,sch_inc=l_sch_mnt))
            if create_recipients:
                SchMntAdditionalRecipients.objects.bulk_create(create_recipients)   
            if Subscriber_list:
                
                l_mass_email=[]
                subscribers_email = list(Subscribers.objects.filter(
                    subscriber_id__in=Subscriber_list).values_list('email','subscriber_token'))
                l_status = str(l_sch_mnt.status).capitalize()
                context = {
                        "incident_data": l_sch_mnt,
                        "component_data": components_effected,
                        "user": user.email,
                        "businessunit":l_businessunit_name,
                        "status":l_status
                }
                # x = datetime.now().strftime("%x %I:%M %p")
                l_status = str(l_sch_mnt.status).capitalize()
                subject = f"[{l_businessunit_name} platform status updates] Scheduled Maintenance {l_status} - Admin"
                
                l_mass_email.append(send_email(
                    template="scheduled_maintenance_email_notification.html",
                    subject=subject,
                    context_data=context,
                    recipient_list=[user.email]+recipients
                ))
                
                for email,token in subscribers_email:
                    context["unsubscribe_url"]="http://18.118.80.163/Status/"+l_businessunit_name+'/unsubscribe/'+token
                    l_mass_email.append(send_email(
                        template="scheduled_maintenance_email_notification.html",
                        subject=subject,
                        context_data=context,
                        recipient_list=[email]
                    ))
                    
                send_mass_mail(l_mass_email) 
                
        return l_sch_mnt
    
    @transaction.atomic
    def update(self, instance, validated_data):
        l_businessunit_name = self.context['request'].headers.get(
            'businessunit')
        user = self.context['request'].user
        initialdata=self.initial_data.get('components')
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True).first()
        
        instance.name = validated_data.get('name', instance.name)
        instance.status = validated_data.get('status', instance.status)
        instance.message = validated_data.get('message', instance.message)
        instance.schstartdate = validated_data.get('schstartdate', instance.schstartdate)
        instance.schenddate = validated_data.get('schenddate', instance.schenddate)
        instance.businessunit=businessunit_qs
        if instance.status=='Completed':
            instance.is_done=1
        instance.save()
        # insert into activity history table
        SchMntActivity.objects.create(
                    sch_inc_id=instance.pk,
                    name=instance.name,
                    status=instance.status,
                    message=instance.message,
                    schstartdate=instance.schstartdate,
                    schenddate=instance.schenddate,
                    createduser_id=user.pk
                )        
        sch_mnt_component_obj=SchMntComponent.objects.filter(sch_inc=instance,businessunit=businessunit_qs)
        l_components=[]
        l_components+=initialdata
        # l_components=[]
        # for comp in components:
        #     l_components.append(comp.get('component_id'))
        sch_mnt_component_create=[]
        if not l_components:
            raise ValidationError({"Error":"Please select atleast one component"})
        try:
            if sch_mnt_component_obj:
                for sch_cmp_obj in sch_mnt_component_obj:
                    if sch_cmp_obj.component_id in l_components:
                        if sch_cmp_obj.is_active:
                            l_components.remove(sch_cmp_obj.component_id)
                            continue
                        sch_cmp_obj.is_active=True
                        l_components.remove(sch_cmp_obj.component_id)
                    else:
                        sch_cmp_obj.is_active=False
                    sch_cmp_obj.save()
                    
            if l_components:
                for cmp_id in l_components:
                    sch_mnt_component_create.append(SchMntComponent(
                sch_inc=instance,
                component_id=cmp_id,
                is_active=True,
                businessunit=instance.businessunit))
            if sch_mnt_component_create:
                sch_mnt_cmp_obj = SchMntComponent.objects.bulk_create(sch_mnt_component_create)
            if not instance.status=='Scheduled':
                Components.objects.filter(businessunit=instance.businessunit,is_active=True,component_id__in=l_components).update(component_status=ComponentsStatus.objects.filter(component_status_name='Under Maintenance').first())
            components_list=initialdata
            components_effected=[]
            Subscriber_list=[]
            for cmp_sts in components_list:
                # We have to get the component subscribers from incident created
                subcomp_obj = list(SubcriberComponent.objects.filter(
                    component_id=cmp_sts, businessunit=businessunit_qs, is_active=True).values_list('subscriber__subscriber_id', flat=True))
                if subcomp_obj:
                    Subscriber_list += (subcomp_obj)
                component_obj=Components.objects.filter(component_id=cmp_sts).first()
                components_effected.append(component_obj.component_name)
                # need to get list of component names that are effected
            
            # Adding additional recipients
            recipients = self.initial_data.get('recipients', [])
            create_recipients=[]
            if recipients:
                for mail in recipients:
                    sch_inc_emails=SchMntAdditionalRecipients.objects.filter(sch_inc=instance,email=mail).first()
                    if not sch_inc_emails:
                        create_recipients.append(SchMntAdditionalRecipients(email=mail,is_active=True,sch_inc=instance))
                    else:
                        if not  sch_inc_emails.is_active:
                            sch_inc_emails.is_active=True
                            sch_inc_emails.save()
            
            SchMntAdditionalRecipients.objects.filter(Q(sch_inc=instance),~Q(email__in=recipients)).update(is_active=False)
            if create_recipients:
                SchMntAdditionalRecipients.objects.bulk_create(create_recipients)
            if Subscriber_list:
                
                l_mass_email=[]
                subscribers_email = list(Subscribers.objects.filter(
                    subscriber_id__in=Subscriber_list).values_list('email','subscriber_token'))
                l_status = str(instance.status).capitalize()
                context = {
                    "incident_data": instance,
                    "component_data": components_effected,
                    "user": user.email,
                    "businessunit":l_businessunit_name,
                    "status":l_status
                }
                x = datetime.now().strftime("%x %I:%M %p")
                l_status = str(instance.status).capitalize()
                subject = f"[{l_businessunit_name} platform status updates] Scheduled Maintenance {l_status} - Admin"
                
                
                l_mass_email.append(send_email(
                    template="scheduled_maintenance_email_notification.html",
                    subject=subject,
                    context_data=context,
                    recipient_list=[user.email]+recipients
                ))
                
                for email,token in subscribers_email:
                    context["unsubscribe_url"]="http://18.118.80.163/Status/"+l_businessunit_name+'/unsubscribe/'+token
                    l_mass_email.append(send_email(
                        template="scheduled_maintenance_email_notification.html",
                        subject=subject,
                        context_data=context,
                        recipient_list=[email]
                    ))
                    
                send_mass_mail(l_mass_email)
                    
        except Exception as e:
            return e
        return instance
    
    
class SchMntActivitySerializer(serializers.ModelSerializer):
    createduser = serializers.SerializerMethodField()
    
    def get_createduser(self, obj):
        return get_cached_user(obj.createduser_id)

    class Meta:
        model = SchMntActivity
        fields = '__all__'
        
        
class IncidentTemplateSerializer(serializers.ModelSerializer):
    businessunit = BusinessUnitSerializer(required=False)
    createduser = serializers.SerializerMethodField()
    modifieduser = serializers.SerializerMethodField()
    
    def get_createduser(self, obj):
        return get_cached_user(obj.createduser_id)

    def get_modifieduser(self, obj):
        return get_cached_user(obj.modifieduser_id)
    class Meta:
        model = IncidentTemplate
        fields = '__all__'
        
    @transaction.atomic
    def create(self, validated_data):
        l_businessunit_name = self.context['request'].headers.get(
            'businessunit')
        user = self.context['request'].user
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True).first()
        validated_data['businessunit'] = businessunit_qs
        validated_data['createduser'] = user
        validated_data['modifieduser'] = user
        try:
    
            l_sch_mnt = super().create(validated_data)
        except Exception as e:
            return e
        
        return l_sch_mnt
    
    @transaction.atomic
    def update(self, instance, validated_data):
        l_businessunit_name = self.context['request'].headers.get(
            'businessunit')
        user = self.context['request'].user
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True).first()
        if not businessunit_qs:
            raise ValidationError({"Error":"Businessunit is not found or not in a active businessunit "})
        try:
            instance.template_name = validated_data.get('template_name', instance.template_name)
            instance.incident_title = validated_data.get('incident_title', instance.incident_title)
            instance.description = validated_data.get('description', instance.description)
            instance.modified_datetime = datetime.now()
            instance.modifieduser = user
            instance.businessunit=businessunit_qs
            instance.save()
       
        except Exception as e:
            return e
        return instance
    
