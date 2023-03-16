from typing import Dict

from django.db import models
from django.db.models import Case, Max, Q, QuerySet, Value, When
from django.db.models.functions import Now, TruncDate
from django.utils.translation import gettext_lazy as _

from api.constants import LICENSES_PERIODS_STATUSES, LICENSE_PERIOD_STATUS_ACTIVE, LICENSE_PERIOD_STATUS_INACTIVE
from api.mixins import ModelTimeStampMixin
from api.models.Employee import Employee
from api.models.Subscription import Subscription


class EmployeeLicenseManager(models.Manager["EmployeeLicense"]):
    def get_queryset(self) -> "QuerySet[EmployeeLicense]":
        """Annotates each LicensePeriod with its `status`"""
        query_set: "QuerySet[EmployeeLicense]" = super().get_queryset().annotate(**self.get_status_annotation_kwargs())
        return query_set

    @staticmethod
    def get_status_annotation_kwargs(join_prefix: str = "") -> Dict[str, Max]:
        """Get status annotation Q object. Allows for reuse of annotation with complex joins."""
        now = TruncDate(Now())
        return {
            f"{join_prefix}status": Max(
                Case(
                    When(
                        (Q(**{f"{join_prefix}start_date__isnull": False}) & Q(**{f"{join_prefix}start_date__gt": now}))
                        | (Q(**{f"{join_prefix}end_date__isnull": False}) & Q(**{f"{join_prefix}end_date__lt": now}))
                        | (
                            Q(**{f"{join_prefix}subscription__start_date__isnull": False})
                            & Q(**{f"{join_prefix}subscription__start_date__gt": now})
                        )
                        | (
                            Q(**{f"{join_prefix}subscription__end_date__isnull": False})
                            & Q(**{f"{join_prefix}subscription__end_date__lt": now})
                        ),
                        then=Value(LICENSE_PERIOD_STATUS_INACTIVE),
                    ),
                    default=Value(LICENSE_PERIOD_STATUS_ACTIVE),
                    output_field=models.SmallIntegerField(choices=LICENSES_PERIODS_STATUSES),
                )
            )
        }


class EmployeeLicense(ModelTimeStampMixin, models.Model):
    """
    A relationship model between Employee and Subscription called EmployeeLicense .
    Args:
        - employee (FK): Reference to Employee
        - subscription (FK): Reference to Subscription
        - start_date (DateField): the license start date
        - end_date (DateField): the license end date
    """

    objects: models.Manager = EmployeeLicenseManager()

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="employees_licenses")
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="employees_licenses")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Employees Licenses")
        db_table = "employees_licenses"

    def get_status(self) -> int:
        """
        Returns the status ID of this EmployeeLicense.
        Can be active (1) or inactive (2).
        """
        if not hasattr(self, "status"):
            return EmployeeLicense.objects.get(id=self.id).status
        return self.status

    def __str__(self) -> str:
        result = f"{self.employee.__str__()} - {self.subscription.__str__()}"
        if self.start_date:
            result += self.start_date.strftime("%m-%d-%Y")
        if self.end_date:
            result += f"- {self.end_date.strftime('%m-%d-%Y')}"
        return result
