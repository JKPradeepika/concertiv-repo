from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.Buyer import Buyer
from api.models.Supplier import Supplier


class BusinessDeal(ModelTimeStampMixin, models.Model):
    """
    A relationship between a Buyer and a Supplier over time.
    In general, there should only be one BusinessDeal for any given Buyer-Supplier pair.
    Each BusinessDeal will typically then include one or more Subscriptions
    to one or more Products. For more information, please see the data model diagrams in
    Concertiv's Lucidcharts account:

    https://lucid.app/documents#/documents?folder_id=272894003

    Args:
        - buyer (ForeignKey): The buyer associated with this BusinessDeal
        - supplier (ForeignKey): The supplier associated with this BusinessDeal
    """

    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Businesses Deals")
        db_table = "business_deals"

    def __str__(self) -> str:
        return f"{self.buyer} ~ {self.supplier}"
