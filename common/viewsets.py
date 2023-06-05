import datetime

from django.db import transaction
from django.db.models import Max, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.account_models import Users
from account.utils import get_hashed_password
from common.mailer import send_email, send_mass_mail
from common.models import (
    Businessunits,
    Components,
    ComponentsStatus,
    IncidentAdditionalRecipients,
    IncidentComponent,
    Incidents,
    IncidentsActivity,
    IncidentsComponentActivitys,
    IncidentTemplate,
    ScheduledMaintenance,
    SchMntComponent,
    Smsgateway,
    SubcriberComponent,
    Subscribers,
)
from common.serializers import (
    BusinessUnitSerializer,
    ComponentsSerializer,
    IncidentsActivitySerializer,
    IncidentSerializer,
    IncidentTemplateSerializer,
    ScheduledMaintanenceSerializer,
    SubscribersSerializer,
)
from common.utils import get_component_status


class BusinessunitViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Businessunits.objects.all()
    serializer_class = BusinessUnitSerializer
    pagination_class=None

    @transaction.atomic
    @action(detail=True, methods=["patch"], url_path="inactive_businessunit")
    def inactive_businessunit(self, request, pk=None):
        user = Users.objects.get(email=request.user.username)
        try:
            businessunit_obj = self.get_object()
            businessunit_obj.modifieduser = user
            serializer = self.serializer_class(
                businessunit_obj, request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class IncidentsViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = IncidentSerializer

    def get_queryset(self):
        l_businessunit = self.request.headers.get("businessunit")
        queryset = Incidents.objects.filter(
            businessunit__businessunit_name=l_businessunit,
            is_active=True,
            isdeleted=False,
        )
        return queryset

    @transaction.atomic
    @action(detail=True, methods=["put"], url_path="update_incident")
    def update_incident(self, request, pk=None):
        input_data = request.data
        new_components = input_data.get("components", None)
        uncheck_components = input_data.get("uncheck_component", None)
        l_incident = self.get_object()
        l_businessunit_name = request.headers.get("businessunit")
        Subscriber_list = []
        # user = request.user
        user = Users.objects.get(email=request.user.username)
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True
        ).first()
        l_incident.businessunit = businessunit_qs
        l_incident.modifieduser = user
        l_incident.modified_datetime = datetime.datetime.now()
        serializer = self.serializer_class(l_incident, input_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            l_incident_activity = IncidentsActivity.objects.create(
                incident_id=l_incident.pk,
                incident_name=l_incident.name,
                message=l_incident.message,
                status=l_incident.status,
                businessunit_id=l_incident.businessunit_id,
                createduser_id=user.user_id,
                modifieduser_id=user.user_id,
                created_datetime=datetime.datetime.now(),
                modified_datetime=datetime.datetime.now(),
                impact_severity=l_incident.impact_severity,
                acer_number=l_incident.acer_number,
                start_time=l_incident.start_time,
                end_time=l_incident.end_time,
                issue_impact=l_incident.issue_impact,
            )
            # inc_comp_obj = IncidentComponent.objects.filter(incident=pk)
            inc_comp_update = []
            inc_comp_create = []
            component_update = []
            l_incident_components_activity = []
            components_effected = []
            l_datetime = datetime.datetime.now()
            if new_components:

                for new_comp_obj in new_components:  # Componets obj list
                    inc_comp_qs = IncidentComponent.objects.filter(
                        incident=pk, component=new_comp_obj.get("component_id")
                    ).first()
                    qs_component = Components.objects.get(
                        pk=new_comp_obj.get("component_id")
                    )
                    l_status_id = get_component_status(
                        new_comp_obj.get("component_status")
                    )
                    if inc_comp_qs:
                        # So we have the recor for this component and incident we need to do check weather status is changed or not
                        # status check
                        # If incident component object is inactive then we need to update that object
                        if not inc_comp_qs.is_active:
                            inc_comp_qs.is_active = True
                            inc_comp_qs.modify_datetime = l_datetime
                            inc_comp_update.append(inc_comp_qs)

                        if (
                            qs_component
                            and not qs_component.component_status_id == l_status_id
                        ):  # if status not match
                            # Update components status if it is updated in incident
                            qs_component.modifieduser = user
                            qs_component.component_status_id = l_status_id
                            component_update.append(qs_component)

                    else:
                        # create a new object incident and update the status
                        inc_comp_create.append(
                            IncidentComponent(
                                incident=l_incident,
                                component_id=new_comp_obj.get("component_id"),
                                is_active=True,
                                created_datetime=l_datetime,
                                modify_datetime=l_datetime,
                                businessunit_id=businessunit_qs.pk,
                            )
                        )
                        if qs_component:
                            qs_component.modifieduser = user
                            qs_component.component_status_id = l_status_id
                            component_update.append(qs_component)

                    components_effected.append(qs_component.component_name)
                    subcomp_obj = list(
                        SubcriberComponent.objects.filter(
                            component_id=new_comp_obj.get("component_id"),
                            businessunit=businessunit_qs,
                            is_active=True,
                        ).values_list("subscriber__subscriber_id", flat=True)
                    )
                    if subcomp_obj:
                        Subscriber_list += subcomp_obj

                    l_incident_components_activity.append(
                        IncidentsComponentActivitys(
                            incidents_activity_id=l_incident_activity.pk,
                            component_id=qs_component.component_id,
                            component_name=qs_component.component_name,
                            component_status=new_comp_obj.get("component_status"),
                            component_status_id=l_status_id,
                            createduser_id=user.user_id,
                            created_datetime=datetime.datetime.now(),
                            incident_id=l_incident.pk,
                        )
                    )

            if uncheck_components:
                for uncheck_comp_data in uncheck_components:
                    IncidentComponent.objects.filter(
                        incident_id=pk, component_id=uncheck_comp_data["component_id"]
                    ).update(is_active=False, modify_datetime=l_datetime)

            if component_update:
                comp_obj = Components.objects.bulk_update(
                    component_update,
                    fields=[
                        "modifieduser",
                        "component_status",
                    ],
                )

            # Adding additional recipients
            recipients = input_data.get("recipients", [])
            create_recipients = []
            if recipients:
                for mail in recipients:
                    inc_emails = IncidentAdditionalRecipients.objects.filter(
                        incident=l_incident, email=mail
                    ).first()
                    if not inc_emails:
                        create_recipients.append(
                            IncidentAdditionalRecipients(
                                email=mail, is_active=True, incident=l_incident
                            )
                        )
                    else:
                        if not inc_emails.is_active:
                            inc_emails.is_active = True
                            inc_emails.save()
                IncidentAdditionalRecipients.objects.filter(
                    Q(incident=l_incident), ~Q(email__in=recipients)
                ).update(is_active=False)
            if create_recipients:
                IncidentAdditionalRecipients.objects.bulk_create(create_recipients)
            if inc_comp_update:
                IncidentComponent.objects.bulk_update(
                    inc_comp_update,
                    fields=[
                        "modify_datetime",
                        "is_active",
                    ],
                )
            if inc_comp_create:
                IncidentComponent.objects.bulk_create(inc_comp_create)
            if l_incident_components_activity:
                IncidentsComponentActivitys.objects.bulk_create(
                    l_incident_components_activity
                )
            if Subscriber_list:

                l_mass_email = []
                subscribers_email = list(
                    Subscribers.objects.filter(
                        subscriber_id__in=Subscriber_list
                    ).values_list("email", "subscriber_token")
                )
                l_status = str(l_incident.status).capitalize()
                context = {
                    "incident_data": l_incident,
                    "component_data": components_effected,
                    "user": user.email,
                    "businessunit": l_businessunit_name,
                    "status": l_status,
                }
                # x = datetime.now().strftime("%x %I:%M %p")
                l_status = str(l_incident.status).capitalize()
                subject = f"[{l_businessunit_name} platform status updates] Incident {l_status} - Admin [ACER No# {l_incident.acer_number}]"

                l_mass_email.append(
                    send_email(
                        template="incident_email_notification.html",
                        subject=subject,
                        context_data=context,
                        recipient_list=[user.email] + recipients,
                    )
                )

                for email, token in subscribers_email:
                    context["unsubscribe_url"] = (
                        "http://18.118.80.163/Status/"
                        + l_businessunit_name
                        + "/unsubscribe/"
                        + token
                    )
                    l_mass_email.append(
                        send_email(
                            template="incident_email_notification.html",
                            subject=subject,
                            context_data=context,
                            recipient_list=[email],
                        )
                    )

                send_mass_mail(l_mass_email)

            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"], url_path="postmorterm")
    def postmorterm_incident(self, request, pk=None):
        input_data = request.data
        user = Users.objects.get(email=request.user.username)
        if input_data is None or input_data.get("incident_postmortem") is None:
            raise ValidationError(
                {
                    "incident_postmortem": "incident postmortem either in the payload or should not be None or empty string."
                }
            )
        l_incident = self.get_object()
        l_incident.modifieduser = user
        serializer = self.serializer_class(l_incident, input_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path="delete_incident")
    def delete_incident(self, request, pk=None):
        l_incident = self.get_object()
        user = Users.objects.get(email=request.user.username)
        try:
            # deleted_obj = Incidents.objects.filter(pk=pk).update(isdeleted=True,
            #  modifieduser=request.user, modify_datetime=datetime.datetime.now())
            l_incident.isdeleted = True
            l_incident.modifieduser = user
            l_incident.modify_datetime = datetime.datetime.now()
            l_incident.save()
            IncidentComponent.objects.filter(
                incident=l_incident,
            ).update(is_active=False, modify_datetime=datetime.datetime.now())
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class ComponentsViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Components.objects.all()
    serializer_class = ComponentsSerializer

    def get_queryset(self):

        l_businessunit = self.request.headers.get("businessunit")
        queryset = Components.objects.filter(
            businessunit__businessunit_name=l_businessunit, is_active=True
        )
        return queryset

    @action(detail=False, methods=["get"], url_path="group_components")
    def group_component(self, request, pk=None):
        group_components = []
        queryset = self.get_queryset()
        queryset = queryset.filter(has_subgroup=True, is_group=True)
        serializer = self.serializer_class(queryset, many=True)
        if serializer.data:
            group_components = serializer.data
        return Response(group_components, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="create_component")
    def create_component(self, request, pk=None):
        input_data = request.data
        l_businessunit_name = request.headers.get("businessunit")
        # user = request.user
        user = Users.objects.get(email=request.user.username)
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True
        ).first()
        # check for component and  grouptype
        if not input_data.get("component_name"):
            raise ValidationError({"Error": "Please provide component name"})
        component_create = []
        if input_data.get("component_name"):
            cmp_orders = Components.objects.filter(
                businessunit=businessunit_qs
            ).aggregate(Max("group_no"), Max("display_order"))
            l_group_no__max = 0
            l_display_order__max = 0

            if cmp_orders["group_no__max"]:
                l_group_no__max = cmp_orders["group_no__max"]
            if cmp_orders["display_order__max"]:
                l_display_order__max = cmp_orders["display_order__max"]

            l_ComponentsStatus = ComponentsStatus.objects.filter(
                component_status_name="Operational"
            ).first()
            if input_data.get("new_group_name"):
                new_group_name = input_data.get("new_group_name")
                # new group component  creation
                component_create.append(
                    Components(
                        component_name=new_group_name,
                        description="",
                        is_group=True,
                        group_no=l_group_no__max + 1,
                        display_order=l_display_order__max + 1,
                        subgroup_display_order=0,
                        businessunit=businessunit_qs,
                        createduser=user,
                        modifieduser=user,
                        has_subgroup=True,
                        component_status=l_ComponentsStatus,
                    )
                )
                # new component creation from the new group component
                component_create.append(
                    Components(
                        component_name=input_data.get("component_name"),
                        description=input_data.get("description"),
                        is_group=False,
                        group_no=l_group_no__max + 1,
                        display_order=l_display_order__max + 1,
                        subgroup_display_order=1,
                        businessunit=businessunit_qs,
                        createduser=user,
                        modifieduser=user,
                        has_subgroup=False,
                        component_status=l_ComponentsStatus,
                    )
                )

            elif input_data.get("component_group"):
                component_obj = Components.objects.get(
                    pk=input_data.get("component_group")
                )
                l_subgroup_display_order = Components.objects.filter(
                    group_no=component_obj.group_no, businessunit=businessunit_qs
                ).aggregate(Max("subgroup_display_order"))
                component_create.append(
                    Components(
                        component_name=input_data.get("component_name"),
                        description=input_data.get("description"),
                        is_group=False,
                        group_no=component_obj.group_no,
                        display_order=component_obj.display_order,
                        subgroup_display_order=l_subgroup_display_order[
                            "subgroup_display_order__max"
                        ]
                        + 1,
                        businessunit=businessunit_qs,
                        createduser=user,
                        modifieduser=user,
                        has_subgroup=False,
                        component_status=l_ComponentsStatus,
                    )
                )
            else:

                component_create.append(
                    Components(
                        component_name=input_data.get("component_name"),
                        description=input_data.get("description"),
                        is_group=True,
                        group_no=l_group_no__max + 1,
                        display_order=l_display_order__max + 1,
                        subgroup_display_order=1,
                        businessunit=businessunit_qs,
                        createduser=user,
                        modifieduser=user,
                        has_subgroup=False,
                        component_status=l_ComponentsStatus,
                    )
                )
        try:
            if component_create:
                Components.objects.bulk_create(component_create)
                return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"], url_path="update_component")
    def update_component(self, request, pk=None):
        input_data = request.data
        user = Users.objects.get(email=request.user.username)
        l_component = self.get_object()
        l_businessunit_name = request.headers.get("businessunit")
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True
        ).first()
        try:
            cmp_orders = Components.objects.filter(
                businessunit=businessunit_qs
            ).aggregate(Max("group_no"), Max("display_order"))
            if not l_component:
                raise ValidationError(
                    {
                        "Error": "component not found in database please provide valid component id"
                    }
                )
            if l_component.is_group and l_component.has_subgroup:
                # Update the group component
                input_data["modifieduser"] = user.pk
                serializer = self.serializer_class(
                    l_component, data=input_data, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Update the sub group component
                if input_data.get("component_group"):

                    group_component_qs = Components.objects.get(
                        pk=input_data.get("component_group")
                    )
                    if group_component_qs:
                        input_data["is_group"] = False
                        input_data["group_no"] = group_component_qs.group_no
                        input_data["display_order"] = group_component_qs.display_order
                        input_data["subgroup_display_order"] = (
                            Components.objects.filter(
                                group_no=group_component_qs.group_no,
                                businessunit=businessunit_qs,
                            )
                            .aggregate(Max("subgroup_display_order"))
                            .get("subgroup_display_order__max")
                            + 1
                        )
                        input_data["has_subgroup"] = False

                        l_component_count = Components.objects.filter(
                            group_no=l_component.group_no, businessunit=businessunit_qs
                        ).count()
                        if l_component_count and l_component_count <= 2:
                            group_component = Components.objects.filter(
                                group_no=l_component.group_no,
                                is_group=True,
                                has_subgroup=True,
                                businessunit=businessunit_qs,
                            ).first()
                            if group_component:
                                group_component.subgroup_display_order = 1
                                group_component.modifieduser = user
                                group_component.has_subgroup = False
                                group_component.save()

                elif input_data.get("new_group_name"):
                    new_group_name = input_data.get("new_group_name")
                    # new group component  creation

                    l_ComponentsStatus = ComponentsStatus.objects.filter(
                        component_status_name="Operational"
                    ).first()
                    new_group = Components.objects.create(
                        component_name=new_group_name,
                        description="",
                        is_group=True,
                        group_no=int(cmp_orders["group_no__max"]) + 1,
                        display_order=int(cmp_orders["display_order__max"]) + 1,
                        subgroup_display_order=0,
                        businessunit=businessunit_qs,
                        createduser=user,
                        modifieduser=user,
                        has_subgroup=True,
                        component_status=l_ComponentsStatus,
                    )
                    if new_group:
                        if input_data.get("component_name"):
                            input_data["component_name"] = input_data.get(
                                "component_name"
                            )
                        if input_data.get("description"):
                            input_data["description"] = input_data.get("description")
                    input_data["is_group"] = False
                    input_data["group_no"] = cmp_orders["group_no__max"] + 1
                    input_data["display_order"] = cmp_orders["display_order__max"] + 1
                    input_data["subgroup_display_order"] = 1

                    l_component_count = Components.objects.filter(
                        group_no=l_component.group_no, businessunit=businessunit_qs
                    ).count()
                    if l_component_count and l_component_count <= 2:
                        group_component = Components.objects.filter(
                            group_no=l_component.group_no,
                            is_group=True,
                            has_subgroup=True,
                            businessunit=businessunit_qs,
                        ).first()
                        if group_component:
                            group_component.subgroup_display_order = 1
                            group_component.modifieduser = user
                            group_component.has_subgroup = False
                            group_component.save()

                else:
                    input_data["is_group"] = True
                    input_data["group_no"] = cmp_orders["group_no__max"] + 1
                    input_data["display_order"] = cmp_orders["display_order__max"] + 1
                    input_data["subgroup_display_order"] = 0
                    input_data["has_subgroup"] = False

                    l_component_count = Components.objects.filter(
                        group_no=l_component.group_no, businessunit=businessunit_qs
                    ).count()
                    if l_component_count and l_component_count <= 2:
                        group_component = Components.objects.filter(
                            group_no=l_component.group_no,
                            is_group=True,
                            has_subgroup=True,
                            businessunit=businessunit_qs,
                        ).first()
                        if group_component:
                            group_component.subgroup_display_order = 1
                            group_component.modifieduser = user
                            group_component.has_subgroup = False
                            group_component.save()

                input_data["modifieduser"] = user.pk
                serializer = self.serializer_class(
                    l_component, data=input_data, partial=True
                )
                if serializer.is_valid():
                    # while updating the component if group component is changes then we need to look at the current updating component
                    # which is under sub group and if the sub group is has only one sub component then we need to update  sub group to component

                    serializer.save()
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path="delete_component")
    def delete_component(self, request, pk=None):
        # user=request.user
        l_component = self.get_object()
        l_businessunit_name = request.headers.get("businessunit")
        # user = request.user
        user = Users.objects.get(email=request.user.username)
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit_name, is_active=True
        ).first()
        try:
            # check deleting object is group component or sub group component
            if l_component.is_group and l_component.has_subgroup:
                # if group component then we need to update the sub group componet which are belong to this group component as independent components
                sub_components_qs = Components.objects.filter(
                    group_no=l_component.group_no, businessunit=businessunit_qs
                ).filter(~Q(component_id=l_component.pk))
                if sub_components_qs:
                    for qs in sub_components_qs:

                        cmp_orders = Components.objects.filter(
                            businessunit=businessunit_qs
                        ).aggregate(Max("group_no"), Max("display_order"))

                        l_group = int(cmp_orders["group_no__max"]) + 1
                        l_display_order = int(cmp_orders["display_order__max"]) + 1
                        # Update sub components
                        qs.is_group = 1
                        qs.group_no = l_group
                        qs.display_order = l_display_order
                        qs.modifieduser = user
                        qs.subgroup_display_order = 0
                        qs.save()
            deleted_obj = l_component.delete()
            return Response(deleted_obj, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class IncidentsActivityViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = IncidentsActivitySerializer
    queryset = IncidentsActivity.objects.all()

    @action(detail=False, methods=["put"], url_path="incident_activity")
    def incident_activity_on_incident_id(self, request, pk=None):
        input_data = request.data
        if input_data is None or input_data.get("incident_id") is None:
            raise ValidationError(
                {"incident_id": "incident id is required in payload."}
            )
        queryset = self.get_queryset()
        l_queryset = queryset.filter(
            incident_id=input_data.get("incident_id")
        ).order_by("-modified_datetime")
        serializer = self.serializer_class(l_queryset, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscribersViewset(viewsets.ModelViewSet):
    serializer_class = SubscribersSerializer
    queryset = Subscribers.objects.all()

    def get_queryset(self):
        l_businessunit = self.request.headers.get("businessunit")
        queryset = Subscribers.objects.filter(
            businessunit__businessunit_name=l_businessunit, is_active=True
        )
        return queryset

    @action(detail=False, methods=["post"], url_path="create_subscriber")
    def create_subsciber_on_businessunit(self, request, pk=None):
        serializer = self.serializer_class(
            data=request.data,
            context={"businessunit": self.request.headers.get("businessunit")},
        )
        if serializer.is_valid(raise_exception=True):
            l_serializer = serializer.create(serializer.validated_data)
            if l_serializer:
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["put"],
        url_path="subscriberslist",
        permission_classes=[IsAuthenticated],
    )
    def get_subscribers(self, request, pk=None):
        inputdata = request.data
        queryset = self.get_queryset()
        if inputdata.get("email_delivery"):
            queryset = queryset.filter(
                email_delivery=inputdata["email_delivery"], is_active=True
            )
        elif inputdata.get("sms_delivery"):
            queryset = queryset.filter(
                sms_delivery=inputdata["sms_delivery"], is_active=True
            )
        else:
            raise ValidationError({"Error": "Subscriber type is required in payload"})
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["patch"],
        url_path="update_subscribers",
        permission_classes=[IsAuthenticated],
    )
    def admin_update_subscribers(self, request, pk=None):
        inputdata = request.data
        if not inputdata.get("components"):
            raise ValidationError({"Error": "Please select atleast one component"})
        subscriber = self.get_object()
        l_businessunit = self.request.headers.get("businessunit")
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit, is_active=True
        ).first()
        subscriber_component_create = []
        subscriber_component_obj = SubcriberComponent.objects.filter(
            subscriber=subscriber, businessunit=businessunit_qs
        )
        l_components_list = inputdata.get("components")
        try:
            if subscriber_component_obj:
                for sub_cmp_obj in subscriber_component_obj:
                    if sub_cmp_obj.component_id in l_components_list:
                        if sub_cmp_obj.is_active:
                            l_components_list.remove(sub_cmp_obj.component_id)
                            continue
                        sub_cmp_obj.is_active = True
                        l_components_list.remove(sub_cmp_obj.component_id)
                    else:
                        sub_cmp_obj.is_active = False
                    sub_cmp_obj.save()

            if l_components_list:
                for cmp_id in l_components_list:
                    subscriber_component_create.append(
                        SubcriberComponent(
                            subscriber_id=subscriber.pk,
                            component_id=cmp_id,
                            is_active=True,
                            businessunit=businessunit_qs,
                        )
                    )
            if subscriber_component_create:
                inc_cmp_obj = SubcriberComponent.objects.bulk_create(
                    subscriber_component_create
                )
                # Just update datetime of subscriber to know last update happen on subsciber
            subscriber.modify_datetime = datetime.datetime.now()
            subscriber.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e, status=status.HTTP_404_NOT_FOUND)

    # This api is used to update subscriber in public page
    @action(detail=False, methods=["patch"], url_path="subscribers_update")
    def update_subscribers(self, request, pk=None):
        inputdata = request.data
        if not inputdata.get("user_token"):
            raise ValidationError({"Error": "Please privide user or user required"})
        if not inputdata.get("components") or not inputdata.get("user_token"):
            raise ValidationError({"Error": "Please select atleast one component"})
        l_businessunit = self.request.headers.get("businessunit")
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit, is_active=True
        ).first()
        if not businessunit_qs:
            raise ValidationError(
                {"Error": "Subscriber doesn't belong to any valid busuiness units"}
            )
        sub_obj = Subscribers.objects.filter(
            subscriber_token=inputdata.get("user_token"),
            businessunit=businessunit_qs,
            is_active=True,
        )
        if not sub_obj:
            raise ValidationError(
                {"Error": "Subscriber not found or subscriber is inactive"}
            )
        subscriber = sub_obj.first()
        subscriber_component_create = []
        subscriber_component_obj = SubcriberComponent.objects.filter(
            subscriber=subscriber, businessunit=businessunit_qs
        )
        l_components_list = inputdata.get("components")
        try:
            if subscriber_component_obj:
                for sub_cmp_obj in subscriber_component_obj:
                    if sub_cmp_obj.component_id in l_components_list:
                        if sub_cmp_obj.is_active:
                            l_components_list.remove(sub_cmp_obj.component_id)
                            continue
                        sub_cmp_obj.is_active = True
                        l_components_list.remove(sub_cmp_obj.component_id)
                    else:
                        sub_cmp_obj.is_active = False
                    sub_cmp_obj.save()

            if l_components_list:
                for cmp_id in l_components_list:
                    subscriber_component_create.append(
                        SubcriberComponent(
                            subscriber_id=subscriber.pk,
                            component_id=cmp_id,
                            is_active=True,
                            businessunit=businessunit_qs,
                        )
                    )
            if subscriber_component_create:
                inc_cmp_obj = SubcriberComponent.objects.bulk_create(
                    subscriber_component_create
                )
                # Just update datetime of subscriber to know last update happen on subsciber
            subscriber.modify_datetime = datetime.datetime.now()
            subscriber.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e, status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=True,
        methods=["delete"],
        url_path="unsubscribe",
        permission_classes=[IsAuthenticated],
    )
    def unsubscribe(self, request, pk=None):
        subscriber_obj = self.get_object()
        if not subscriber_obj:
            raise ValidationError({"Error": "Subscriber not found"})
        # Delete the subscriber
        try:
            l_businessunit = self.request.headers.get("businessunit")
            SubcriberComponent.objects.filter(
                subscriber=subscriber_obj,
                businessunit__businessunit_name=l_businessunit,
            ).delete()
            subscriber_obj.delete()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e, status=status.HTTP_404_NOT_FOUND)

    # This api is used to delete subscriber in public page
    @action(detail=False, methods=["delete"], url_path="unsubscribe_public")
    def unsubscribe_public(self, request, pk=None):
        user_token = request.GET.get("id")
        if not user_token:
            raise ValidationError({"Error": "Please privide user or user required"})
        l_businessunit = self.request.headers.get("businessunit")
        businessunit_qs = Businessunits.objects.filter(
            businessunit_name=l_businessunit, is_active=True
        ).first()
        if not businessunit_qs:
            raise ValidationError(
                {"Error": "Subscriber doesn't belong to any valid busuiness units"}
            )

        sub_obj = Subscribers.objects.filter(
            subscriber_token=user_token, businessunit=businessunit_qs, is_active=True
        )
        if not sub_obj:
            raise ValidationError(
                {"Error": "Subscriber not found or subscriber is inactive"}
            )
        subscriber_obj = sub_obj.first()
        # Delete the subscriber
        try:
            subscriber_components = SubcriberComponent.objects.filter(
                subscriber=subscriber_obj,
                businessunit__businessunit_name=l_businessunit,
            )
            if subscriber_components:
                subscriber_components.delete()
            subscriber_obj.delete()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e, status=status.HTTP_404_NOT_FOUND)


class ScheduledMaintanenceViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ScheduledMaintanenceSerializer
    queryset = ScheduledMaintenance.objects.filter(is_active=True)

    def get_queryset(self):
        l_businessunit = self.request.headers.get("businessunit")
        queryset = ScheduledMaintenance.objects.filter(
            businessunit__businessunit_name=l_businessunit, is_active=True
        )
        return queryset

    @action(detail=True, methods=["delete"], url_path="sch_mnt_del")
    def delete_scheduled_maintenance(self, request, pk=None):

        sch_mnt_obj = self.get_object()
        SchMntComponent.objects.filter(sch_inc=sch_mnt_obj).update(is_active=False)
        sch_mnt_obj.is_active = False
        sch_mnt_obj.save()
        return Response(status=status.HTTP_200_OK)


class IncidentTemplateViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = IncidentTemplateSerializer
    queryset = IncidentTemplate.objects.filter(is_active=True)

    def get_queryset(self):
        l_businessunit = self.request.headers.get("businessunit")
        queryset = IncidentTemplate.objects.filter(
            businessunit__businessunit_name=l_businessunit, is_active=True
        )
        return queryset

    @action(detail=True, methods=["delete"], url_path="inc_temp_del")
    def delete_incident_template(self, request, pk=None):

        inc_temp_obj = self.get_object()
        if inc_temp_obj:
            inc_temp_obj.is_active = False
            inc_temp_obj.save()

        return Response(status=status.HTTP_200_OK)
