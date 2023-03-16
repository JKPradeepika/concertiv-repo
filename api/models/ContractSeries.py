from django.db import models
from django.utils.translation import gettext_lazy as _
from api.mixins import ModelTimeStampMixin


class ContractSeries(ModelTimeStampMixin, models.Model):
    """
    Identifies chains of contracts that have been renewed.
    """

    class Meta:
        verbose_name_plural = _("Contract Series")
        db_table = "contract_series"
