from django.db.models import IntegerChoices


class IncidentStatusChoices(IntegerChoices):
    Investigating = 1
    Identified = 2
    Monitoring = 3
    Resolved = 4
