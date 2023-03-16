from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.Department import Department
from api.models.Employer import Employer


class EmployerDepartment(ModelTimeStampMixin, models.Model):
    """
    EmployerDepartments in Komodo just represent a ManyToMany relationship between employers and departments.
    The name can be overridden.

    EmployerDepartments in Profiler represent departments specific to a certain employer.
    For spend reporting purposes, a department FK can be provided which associates a
    employer-specific department with a global department.

    Args:
        - name (TextField): The name of the department
        - employer (ForeignKey): The Employer to which this EmployerDepartment belongs
        - department (ForeignKey): (optional) The global Department to which this EmployerDepartment
            corresponds. Used for reporting across Employers.
    """

    name = models.TextField()
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Employers Departments")
        db_table = "employers_departments"

    def __str__(self) -> str:
        return self.name
