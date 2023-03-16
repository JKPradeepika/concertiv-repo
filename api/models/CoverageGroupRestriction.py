from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.EmployerCoverageGroup import EmployerCoverageGroup
from api.models.Subscription import Subscription


class CoverageGroupRestriction(ModelTimeStampMixin, models.Model):
    """
    A restriction on which users may access a certain Product based on their CoverageGroup.
    The restricted Product can be accessed via Subscription -> Product.

    Args:
        employer_coverage_group (ForeignKey): The EmployerCoverageGroup to which the Subscription is restricted
        subscription (ForeignKey): The restricted Subscription
    """

    employer_coverage_group = models.ForeignKey(EmployerCoverageGroup, on_delete=models.CASCADE, null=True)
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, null=True, related_name="coverage_group_restrictions"
    )

    class Meta:
        verbose_name_plural = _("Coverage Groups Restrictions")
        db_table = "coverages_groups_restriction"
        constraints = [
            models.UniqueConstraint(
                fields=["employer_coverage_group", "subscription"],
                name="unique_coverage_group_restriction_per_subscription",
            ),
        ]

    def __str__(self) -> str:
        return str(self.employer_coverage_group)
