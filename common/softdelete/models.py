"""This module provides the model mixin for the soft deletion."""
from django.db import models


class SoftDeleteModelMixin(models.Model):
    """Model mixin for the soft deletion."""

    SOFT_DELETE_FIELD = "isdeleted"

    ROLLBACK_PAYLOAD = {SOFT_DELETE_FIELD: False}

    @staticmethod
    def get_delete_payload():
        """Delete payload for soft delete."""
        return {SoftDeleteModelMixin.SOFT_DELETE_FIELD: True, }

    class Meta:
        """Making base class as abstract as it do not require its on db table."""

        abstract = True

    def delete(self, *args, **kwargs):
        """Soft Delete the object."""
        for attr, value in self.get_delete_payload().items():
            setattr(self, attr, value)
            self.save(*args, **kwargs)

    def erase(self, *args, **kwargs):
        """Actually delete from database."""
        return super().delete(*args, **kwargs)

    def restore(self, *args, **kwargs):
        """Restore the  previously soft deleted  object."""
        for attr, value in self.ROLLBACK_PAYLOAD.items():
            setattr(self, attr, value)
            self.save(*args, **kwargs)
