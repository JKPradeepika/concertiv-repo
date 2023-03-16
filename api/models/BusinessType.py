from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin


class BusinessType(ModelTimeStampMixin, models.Model):
    """
    A label that captures what type of business Client, a client is.
    """

    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = _("Business Types")
        db_table = "business_types"

    def __str__(self) -> str:
        return self.name
