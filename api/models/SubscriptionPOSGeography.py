from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.Geography import Geography
from api.models.Subscription import Subscription


class SubscriptionPOSGeography(ModelTimeStampMixin, models.Model):
    """
    Adds ability to map a (travel domain) subscription to multiple
    POS (point of service) geographies.
    """

    geography = models.ForeignKey(Geography, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="pos_geographies")

    class Meta:
        verbose_name_plural = _("Subscription POS Geographies")
        db_table = "subscription_pos_geographies"
        constraints = [
            models.UniqueConstraint(
                fields=["geography", "subscription"],
                name="unique_pos_geography_per_subscription",
            ),
        ]

    def __str__(self) -> str:
        return f"Geography {self.geography.name} - Subscription {self.subscription.id}"
