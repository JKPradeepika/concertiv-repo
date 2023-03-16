from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.EmployeeLevel import EmployeeLevel
from api.models.Employer import Employer


class EmployerEmployeeLevel(ModelTimeStampMixin, models.Model):
    """
    EmployerEmployeeLevels in Komodo just represent a ManyToMany relationship between employers and employee levels.
    The name can be overridden.

    EmployerEmployeeLevels represent employee levels specific to a certain employer.
    For spend reporting purposes, an employee_level FK can be provided which associates a
    employer-specific employee level with a global employee level.

    Args:
        - name (TextField): The name of the employee level
        - employer (ForeignKey): The Employer to which this EmployerEmployeeLevel belongs
        - employee_level (ForeignKey): (optional) The global EmployeeLevel to which this EmployerEmployeeLevel
            corresponds. Used for reporting across Employers.
    """

    name = models.TextField()
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    employee_level = models.ForeignKey(EmployeeLevel, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Employers Employees Levels")
        db_table = "employers_employees_levels"

    def __str__(self) -> str:
        return self.name
