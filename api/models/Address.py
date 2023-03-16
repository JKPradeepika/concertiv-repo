from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin


class Address(ModelTimeStampMixin, models.Model):
    """
    A street address (US-only).
    """

    street1 = models.TextField(blank=True)
    street2 = models.TextField(blank=True)
    city = models.TextField(blank=True)
    state = models.TextField(blank=True)
    country = models.TextField(blank=True)
    postal_code = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = _("Addresses")
        db_table = "addresses"

    def __str__(self) -> str:
        return f"{self.street1} {self.street2}, {self.city}, {self.state}, {self.country} {self.postal_code}"
