from django.db import models
from django.utils.translation import gettext_lazy as _

from api.constants import DOMAIN_MARKET_DATA, DOMAINS
from api.mixins import ModelTimeStampMixin


class ProductType(ModelTimeStampMixin, models.Model):
    """
    A label that captures what type of Product, a product is.
    """

    name = models.TextField()
    domain = models.SmallIntegerField(choices=DOMAINS, default=DOMAIN_MARKET_DATA)

    class Meta:
        verbose_name_plural = _("Products Types")
        db_table = "products_types"

    def __str__(self) -> str:
        return self.name
