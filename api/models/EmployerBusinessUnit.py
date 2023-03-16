from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.Employer import Employer


class EmployerBusinessUnit(ModelTimeStampMixin, models.Model):
    """
    A division of an Employer that is useful to track different business units.
    In Profiler, this table is only used for two Employers: Perella Weinberg & General Atlantic.

    Some example business units:
        - AdCo - unknown
        - AmCo - unknown
        - TopCo - unknown
        - SecCo - unknown

    Args:
        - name (TextField): The name of the business unit
        - employer (TextField): The employer to which this business unit belongs
    """

    name = models.TextField()
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Employers Business Units")
        db_table = "employers_business_units"

    def __str__(self) -> str:
        return self.name
