from rest_framework import serializers, status
from rest_framework.response import Response
from account.services import get_cached_user
from django.db import transaction

from common.models import Businessunits, Components, ComponentsStatus, IncidentComponent, Incidents, SubcriberComponent


class BusinessUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Businessunits
        fields = '__all__'


class ComponentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentsStatus
        fields = '__all__'


class IncidentSerializer(serializers.ModelSerializer):
    businessunit = BusinessUnitSerializer(required=False)
    createduser = serializers.SerializerMethodField()
    modifieduser = serializers.SerializerMethodField()

    def get_createduser(self, obj):
        return get_cached_user(obj.createduser_id)

    def get_modifieduser(self, obj):
        return get_cached_user(obj.modifieduser_id)

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
        if components_list is not None:
            l_inc_com_obj = [IncidentComponent(
                incident_id=l_incident.pk,
                component_id=businessunit_qs.pk,
                is_active=True
            ) for cmp_id in components_list]
            inc_cmp_obj = IncidentComponent.objects.bulk_create(l_inc_com_obj)
            Subcrbcom_obj = SubcriberComponent.objects.filter(
                component_id__in=components_list, businessunit_id=businessunit_qs.pk, is_active=True)
            # TODO
            # Send Mail for the subscriber who subscribed for this components
        return l_incident


class ComponentsSerializer(serializers.ModelSerializer):
    component_status = ComponentStatusSerializer()
    businessunit = BusinessUnitSerializer()

    class Meta:
        model = Components
        fields = '__all__'