from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.Employer import Employer


class EmployerCostCenter(ModelTimeStampMixin, models.Model):
    """
    A division of an Employer that is useful to track for spend reporting.
    In Profiler, this table is only used for two Employers: Perella Weinberg & General Atlantic.

    Args:
        - name (TextField): The name of the cost center
        - employer (TextField): The employer to which this cost center belongs
    """

    name = models.TextField()
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Employers Costs Centers")
        db_table = "employers_costs_centers"

    def __str__(self) -> str:
        return self.name
