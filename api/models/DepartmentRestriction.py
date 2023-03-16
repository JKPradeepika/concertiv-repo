from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.EmployerDepartment import EmployerDepartment
from api.models.Subscription import Subscription


class DepartmentRestriction(ModelTimeStampMixin, models.Model):
    """
    A restriction on which users may access a certain Product based on their Department.
    The restricted Product can be accessed via Subscription -> Product.

    Args:
        employer_department (ForeignKey): The EmployerDepartment to which the Subscription is restricted
        subscription (ForeignKey): The restricted Subscription
    """

    employer_department = models.ForeignKey(EmployerDepartment, on_delete=models.CASCADE)
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, null=True, related_name="department_restrictions"
    )

    class Meta:
        verbose_name_plural = _("Departments Restrictions")
        db_table = "departments_restrictions"
        constraints = [
            models.UniqueConstraint(
                fields=["employer_department", "subscription"],
                name="unique_department_restriction_per_subscription",
            ),
        ]

    def __str__(self) -> str:
        return str(self.employer_department)
