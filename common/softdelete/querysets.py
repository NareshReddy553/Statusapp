"""This module provided the queryset for the soft delete functionality."""
from django.db import models


class SoftDeletionQuerySet(models.QuerySet):
    """Custom queryset for the soft delete functionality."""

    def delete(self):
        """Soft delete the objects in the queryset."""
        return super().update(**self.model.get_delete_payload())

    def erase(self):
        """Delete the objects in the queryset from database."""
        return super().delete()

    def alive(self):
        """Get the non deleted objects from database."""
        return self.exclude(**self.model.get_delete_payload())

    def dead(self):
        """Get the deleted objects from database."""
        return self.filter(**self.model.get_delete_payload())

    def rollback(self):
        """Rollback the deletion status of  objects in the database."""
        return super().update(**self.model.ROLLBACK_PAYLOAD)
