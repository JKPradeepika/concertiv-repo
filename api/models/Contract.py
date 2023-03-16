from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField

from api.constants import (
    CONTRACT_DURATION_UNITS,
    CONTRACT_STATUSES,
    CONTRACT_STATUS_ACTIVE,
)
from api.mixins import ModelTimeStampMixin
from api.models.BusinessDeal import BusinessDeal
from api.models.ContractSeries import ContractSeries


class Contract(ModelTimeStampMixin, models.Model):
    """
    A specific instance of a BusinessDeal, with a `start_date`, `end_date`, and
    associated with one or more `LicensePeriods`. BusinessDeals capture the entire relationship between
    and Buyer and a Supplier over time, whereas Contracts capture changes
    to the terms of the Contract over time (e.g. autorenewal deadline, etc...)

    Args:
        - business_deal (ForeignKey): The BusinessDeal associated with this Contract
        - buyer_entity_name (TextField): The name of the Buyer, as listed on the contract. Generally, the
            `business_entity_name` should match the Buyer name. However, it can be useful to specify a different
            name in certain situations. For instance, when a subsidiary is listed as the actual buyer on a contract.
            Storing the buyer name here even when it matches the buyer's name exactly makes the DB schema
            slightly denormalized; however, this design is intentional, as it keeps historical contracts
            accurate even if the buyer's name changes in the future.
        - start_date (DateField): The date on which this Contract takes effect
        - end_date (DateField): The date on which this Contract ends (inclusive)
        - signed_date (DateField): The date on which this Contract was signed
        - autorenewal_duration (PositiveSmallIntegerField): If `does_autorenew` is true and the Contract
            is not cancelled by the `autorenewal_deadline`, the number of days / weeks / months / years that the
            (automatically) renewed Contract will last.
        - autorenewal_duration_unit (TextField): The unit of the `autorenewal_duration`. E.g. `Days`, `Weeks`,
            `Months`, `Years`.
        - autorenewal_deadline (DateField): If `does_autorenew` is true, the date by which this Contract
            must be cancelled
        - terminated_at: The date on which the Supplier was notified that the Buyer will not be renewing this
            Subscription. Note that having a termination date does not mean that the Subscription has a status of
            "Terminated." The Subscription will remain "Active" the end_date passes, at which point it will be marked
            as "Terminated." The difference between an "Expired" subscription and a "Terminated" subscription is that
            the Buyer intends to renew the "Expired" subscription.
        - precautionary cancellation date: WIP, but supposedly the date at which an autorenewal was cancelled,
            or is to be cancelled
    """

    business_deal = models.ForeignKey(BusinessDeal, on_delete=models.CASCADE, related_name="contracts")
    buyer_entity_name = models.TextField()
    status = models.SmallIntegerField(choices=CONTRACT_STATUSES, default=CONTRACT_STATUS_ACTIVE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    signed_date = models.DateField(null=True, blank=True)
    autorenewal_duration = models.PositiveSmallIntegerField(null=True, blank=True)
    autorenewal_duration_unit = models.SmallIntegerField(choices=CONTRACT_DURATION_UNITS, null=True, blank=True)
    autorenewal_deadline = models.DateField(null=True, blank=True)
    precautionary_cancellation_date = models.DateField(null=True)
    terminated_at = models.DateField(null=True, blank=True)
    calculated_total_price = MoneyField(max_digits=14, decimal_places=2, default_currency="USD", default=0)
    previous_contract = models.ForeignKey("Contract", on_delete=models.SET_NULL, null=True)
    contract_series = models.ForeignKey(ContractSeries, on_delete=models.PROTECT, null=True)
    proposal_price = MoneyField(max_digits=14, decimal_places=2, default_currency="USD", null=True)

    class Meta:
        verbose_name_plural = _("Contracts")
        db_table = "contracts"

    def __str__(self) -> str:
        if not self.start_date:
            return f"{self.business_deal}"
        date_string: str = f"({self.start_date.year}–"
        if self.end_date:
            date_string += f"{self.end_date.year})"
        else:
            date_string += "present)"
        return f"{self.business_deal} {date_string}"

    def get_does_autorenew(self) -> bool:
        """
        Returns:
            bool: `True` if this Contract renews automatically if it is not cancelled by a certain date
        """
        return self.autorenewal_duration is not None
