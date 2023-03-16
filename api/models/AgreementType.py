from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin


class AgreementType(ModelTimeStampMixin, models.Model):
    """
    A label that captures what type of agreement, a product is.
    """

    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = _("Agreements Types")
        db_table = "agreements_types"

    def __str__(self) -> str:
        return self.name
