from datetime import date

from django.db import models
from django.utils.translation import gettext_lazy as _

from api.constants import (
    EMPLOYMENT_STATUS_ACTIVE,
    EMPLOYMENT_STATUS_INACTIVE,
    EMPLOYMENT_STATUS_UPCOMING_DEPARTURE,
    EMPLOYMENT_STATUS_UPCOMING_HIRE,
)
from api.mixins import ModelTimeStampMixin
from api.models.EmployerBusinessUnit import EmployerBusinessUnit
from api.models.EmployerCostCenter import EmployerCostCenter
from api.models.EmployerCoverageGroup import EmployerCoverageGroup
from api.models.EmployerDepartment import EmployerDepartment
from api.models.EmployerEmployeeLevel import EmployerEmployeeLevel
from api.models.EmployerGeography import EmployerGeography
from api.models.Person import Person


class Employee(ModelTimeStampMixin, models.Model):
    """
    A person belonging to an employer to whom we need to attribute spend, etc...
    Args:
        - person (OneToOneField): The associated person object, which stores the employee's email, name, etc...
    """

    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    employer_business_unit = models.ForeignKey(
        EmployerBusinessUnit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employer_cost_center = models.ForeignKey(
        EmployerCostCenter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employer_coverage_group = models.ForeignKey(
        EmployerCoverageGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employer_department = models.ForeignKey(
        EmployerDepartment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employer_employee_level = models.ForeignKey(
        EmployerEmployeeLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employer_geography = models.ForeignKey(
        EmployerGeography,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = _("Employees")
        db_table = "employees"

    def __str__(self) -> str:
        return self.person.__str__()

    @property
    def employment_status(self) -> int:
        hire_date = self.person.hire_date
        departure_date = self.person.termination_date
        today = date.today()

        if departure_date is not None:
            if departure_date <= today:
                return EMPLOYMENT_STATUS_INACTIVE
            return EMPLOYMENT_STATUS_UPCOMING_DEPARTURE

        if hire_date is None or hire_date <= today:
            return EMPLOYMENT_STATUS_ACTIVE
        else:
            return EMPLOYMENT_STATUS_UPCOMING_HIRE
