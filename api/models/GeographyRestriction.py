from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.EmployerGeography import EmployerGeography
from api.models.Subscription import Subscription


class GeographyRestriction(ModelTimeStampMixin, models.Model):
    """
    A restriction on which users may access a certain Product based on their Geography.
    The restricted Product can be accessed via Subscription -> Product.

    Args:
        employer_geography (ForeignKey): The EmployerGeography to which the Subscription is restricted
        subscription (ForeignKey): The restricted Subscription
    """

    employer_geography = models.ForeignKey(EmployerGeography, on_delete=models.CASCADE)
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, null=True, related_name="geography_restrictions"
    )

    class Meta:
        verbose_name_plural = _("Geographies Restrictions")
        db_table = "geographies_restrictions"
        constraints = [
            models.UniqueConstraint(
                fields=["employer_geography", "subscription"],
                name="unique_geography_restriction_per_subscription",
            ),
        ]

    def __str__(self) -> str:
        return self.employer_geography.__str__()
