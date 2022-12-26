"""Custom Save Search manager for SavedSearch model."""
from common.softdelete.querysets import SoftDeletionQuerySet
from django.db import models


class SoftDeleteManger(models.Manager):
    """SoftDeleteManger to soft delete record from database."""

    def get_queryset(self):
        """Override default get queryset to soft delete records from database."""
        return SoftDeletionQuerySet(self.model, using=self._db)
