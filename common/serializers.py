from datetime import datetime
from rest_framework import serializers, status
from rest_framework.response import Response
from account.services import get_cached_user
from django.db import transaction

from common.models import Businessunits, Components, ComponentsStatus, IncidentComponent, Incidents, SubcriberComponent, IncidentsActivity


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
                l_last_component_status = IncidentsActivity.objects.filter(
                    incident_id=obj.pk, component_id=data_obj.component.component_id).order_by('-modified_datetime')

                if data_obj.component.is_active:
                    temp_dict['component_id'] = data_obj.component.component_id
                    temp_dict['component_name'] = data_obj.component.component_name
                    temp_dict['component_status'] = data_obj.component.component_status.component_status_name
                    if l_last_component_status and len(l_last_component_status) >= 1:
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
        l_incident_activity = list()
        if components_list is not None:
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
                Components.objects.filter(pk=cmp_sts.get('component_id')).update(
                    component_status=component_status_obj, modified_datetime=datetime.now(), modifieduser=user)
            inc_cmp_obj = IncidentComponent.objects.bulk_create(l_inc_com_obj)
            # Need entry in the incident activity table each time when we create the incident
            if inc_cmp_obj:
                for inc_cmp_data in inc_cmp_obj:
                    cmp_qs = Components.objects.filter(
                        component_id=inc_cmp_data.component_id).first()
                    l_incident_activity.append(IncidentsActivity(
                        incident_id=l_incident.pk,
                        incident_name=l_incident.name,
                        message=l_incident.message,
                        status=l_incident.status,
                        businessunit_id=l_incident.businessunit_id,
                        component_id=cmp_qs.component_id,
                        component_name=cmp_qs.component_name,
                        component_status=cmp_qs.component_status.component_status_name,
                        component_status_id=cmp_qs.component_status.component_status_id,
                        createduser_id=user.user_id,
                        modifieduser_id=user.user_id,
                        created_datetime=datetime.now(),
                        modified_datetime=datetime.now()))
            if l_incident_activity:
                incident_activity_obj = IncidentsActivity.objects.bulk_create(
                    l_incident_activity)
            # Subcrbcom_obj = SubcriberComponent.objects.filter(
            #     component_id__in=components_list, businessunit_id=businessunit_qs.pk, is_active=True)
            # TODO
            # Send Mail for the subscriber who subscribed for this components
        return l_incident


class IncidentsActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = IncidentsActivity
        fields = '__all__'
