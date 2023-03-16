from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin


class EmployeeLevel(ModelTimeStampMixin, models.Model):
    """
    @args: name (TextField): The name of the employee level
    """

    name = models.TextField()

    class Meta:
        verbose_name_plural = _("Employee Levels")
        db_table = "employees_levels"

    def __str__(self) -> str:
        return self.name
