from typing import Dict

from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField

from api.constants import (
    SUBSCRIPTION_BILLING_FREQUENCIES,
    SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY,
    DOMAINS,
    DOMAIN_MARKET_DATA,
    DISCOUNT_TYPES,
)
from api.mixins import ModelTimeStampMixin
from api.models.Contact import Contact
from api.models.Contract import Contract
from api.models.Product import Product
from api.models.Supplier import Supplier


class SubscriptionManager(models.Manager["Subscription"]):
    def get_queryset(self) -> models.QuerySet["Subscription"]:
        """Includes various annotations."""
        queryset: models.QuerySet["Subscription"] = super().get_queryset().annotate(**self.get_annotation_kwargs())
        return queryset

    @staticmethod
    def get_annotation_kwargs(join_prefix: str = "") -> Dict[str, models.Aggregate]:
        """Get map of key names to Aggregates. Allows for reuse of annotation with complex joins."""
        return {
            join_prefix + "license_period_count": models.Count(join_prefix + "licenses_periods"),
            join_prefix
            + "is_multiterm": models.Case(
                models.When(models.Q(**{f"{join_prefix}license_period_count__gt": 1}), then=models.Value(True)),
                default=models.Value(False),
                output_field=models.BooleanField(),
            ),
            join_prefix + "employee_license_count": models.Count(join_prefix + "employees_licenses"),
            join_prefix
            + "does_autorenew": models.Case(
                models.When(
                    models.Q(**{f"{join_prefix}contract__autorenewal_duration__isnull": True}), then=models.Value(True)
                ),
                default=models.Value(False),
                output_field=models.BooleanField(),
            ),
        }


class Subscription(ModelTimeStampMixin, models.Model):
    """
    An arrangement by which access is granted to a Product over time.

    Multiple Subscriptions can belong to a single Contract.

    Args:
        - contract (Foreign Key): The Contract this Subscription is part of
        - product (ForeignKey): The Product to which this Subscription grants access
        - domain (ForeignKey): The domain to which this subscription is related with
        - contact (ForeignKey): The person at the Supplier who is in charge of managing this Subscription and / or
            selling the associated Product.
        - name (TextField): The name of this Subscription. Generally, the Subscription name should match the Product
            name. However, it can be useful to specify a different name on the Subscription object when a company has
            two Subscriptions to the same Product (e.g. "Bloomberg Terminals (John)" vs. "Bloomberg Terminals (Jane)").
        2 years with an amount of $10,000 and an annual billing_frequency, will the Employer be billed $5,000 twice, or
        will they be billed $10,000 twice?
        - billing_frequency (TextField): The frequency with which the Employer will be billed the given `amount` for
            this LicensePeriod. The default is `Annually`.
        - notes (TextField): Any important information regarding this Subscription.)
        - tax_rate (DecimalField): The tax rate levied against the `price`, stored as a decimal number. For instance,
            a value of `0.0825` translates to an `8.25%` tax rate. To mitigate misuse, the maximum value is currently
            set to `9.999999` (or `999.9999%`).
        - reseller_supplier (ForeignKey): Optional indicator for technology domain subscriptions that a seller is
            reselling a product from another supplier.
    """

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="subscriptions", null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    domain = models.SmallIntegerField(choices=DOMAINS, default=DOMAIN_MARKET_DATA)
    contacts = models.ManyToManyField(Contact, db_table="contracts_subscription_contacts")
    name = models.TextField()
    billing_frequency = models.SmallIntegerField(
        choices=SUBSCRIPTION_BILLING_FREQUENCIES, default=SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY
    )
    notes = models.TextField(blank=True)
    tax_rate = models.DecimalField(max_digits=7, decimal_places=6, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    calculated_total_price = MoneyField(max_digits=14, decimal_places=2, default_currency="USD", default=0)
    reseller_supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, related_name="reseller_supplier"
    )
    tmc_supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name="tmc_supplier")
    discount_type = models.SmallIntegerField(choices=DISCOUNT_TYPES, null=True)
    proposal_price = MoneyField(max_digits=14, decimal_places=2, default_currency="USD", null=True)

    objects = SubscriptionManager()

    class Meta:
        verbose_name_plural = _("Subscriptions")
        db_table = "subscriptions"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        self.domain = self.product.domain
        return super().save(*args, **kwargs)
