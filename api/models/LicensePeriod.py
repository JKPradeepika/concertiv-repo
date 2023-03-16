from typing import Any, cast, Dict, Optional

from django.db import models
from django.db.models import Case, Max, Q, QuerySet, Value, When, Aggregate
from django.db.models.functions import Now, TruncDate
from django.utils.translation import gettext_lazy as _
from django_stubs_ext import WithAnnotations
from djmoney.models.fields import MoneyField
from djmoney.money import Money

from api.constants import (
    LICENSES_PERIODS_TYPES,
    LICENSE_PERIOD_TYPE_OTHER,
    LICENSES_PERIODS_USAGE_UNITS,
    LICENSE_PERIOD_USAGE_UNIT_OTHER,
    LICENSE_PERIOD_STATUS_ACTIVE,
    LICENSE_PERIOD_STATUS_UPCOMING,
    LICENSE_PERIOD_STATUS_INACTIVE,
    LICENSES_PERIODS_STATUSES,
    LICENSE_PERIOD_TYPE_USER_LIMIT,
    LICENSE_PERIOD_TYPE_PER_USER,
)
from api.mixins import ModelTimeStampMixin
from api.models.EmployeeLicense import EmployeeLicense
from api.models.Subscription import Subscription


class LicensePeriodManager(models.Manager["LicensePeriod"]):
    def create(self, *args: Any, **obj_data: Any) -> "LicensePeriod":
        if "exchange_rate_to_usd_at_time_of_purchase" not in obj_data:
            obj_data["exchange_rate_to_usd_at_time_of_purchase"] = 1
        license_period = super().create(**obj_data)
        return license_period

    def get_queryset(self) -> "QuerySet[LicensePeriod]":
        """Annotates each LicensePeriod with its `status`"""
        query_set: "QuerySet[LicensePeriod]" = (
            super(LicensePeriodManager, self).get_queryset().annotate(**self.get_status_annotation_kwargs())
        )
        return query_set

    @staticmethod
    def get_status_annotation_kwargs(join_prefix: str = "") -> Dict[str, Aggregate]:
        """Get status annotation Q object. Allows for reuse of annotation with complex joins."""
        now = TruncDate(Now())
        return {
            join_prefix
            + "status": Max(
                Case(
                    When(
                        Q(**{join_prefix + "start_date__lte": now})
                        & (Q(**{join_prefix + "end_date__gte": now}) | Q(**{join_prefix + "end_date__isnull": True})),
                        then=Value(LICENSE_PERIOD_STATUS_ACTIVE),
                    ),
                    When(**{join_prefix + "start_date__gt": now}, then=Value(LICENSE_PERIOD_STATUS_UPCOMING)),
                    default=Value(LICENSE_PERIOD_STATUS_INACTIVE),
                    output_field=models.CharField(max_length=50, choices=LICENSES_PERIODS_STATUSES),
                )
            ),
        }


class LicensePeriod(ModelTimeStampMixin, models.Model):
    """
    An obligation to spend a certain amount of money for access to a Product (through a Subscription).
    There are many types of LicensePeriods. Some types simply record the fee paid for access
        e.g. "Enterprise," "Minimum Cost," etc...
    Other types, however, also record restrictions on licensing
        e.g. "User Limit" which stipulates the `max_users`that can access the Product

    Note that all cost information is tracked by the `amount` field, the meaning of which changes based on the
    type of the LicensePeriod. For instance, the `amount` field on an "Enterprise" LicensePeriod
    signifies a flat fee paid once (or annually, etc...). In contrast, the `amount` field on an "Incremental User Cost"
    LicensePeriod
    signifies an incremental fee paid for every additional user who gains access to a Product beyond an allotted number
    of licenses.

    To take an example from Profiler, a Cycle (a Profiler concept) with both a `total_cost` and a `cost_per_user`
    will now be split up into two separate LicensePeriods, an "Enterprise" and a "Per User" LicensePeriod,
    each with its own `amount` field.

    Fields dropped from Profiler:
    - implied_cost_per_user (seems like something that should be a DB view)

    Fields renamed from Profiler:
    - max_credits (used to be on the Subscription model)
    - max_users (used to be on the Subscription model)
    - effective_at -> start_date + end_date (although there's an argument to be made for continuing to use effective_at)
    - usd_exchange_rate -> exchange_rate_to_usd_at_time_of_purchase
    - usage_units -> usage_unit
    - total_cost -> amount (captured as the `amount` on ENTERPRISE LicensePeriods)
    - cost_per_user -> amount (captured as the `amount` on PER_USER LicensePeriods)
    - usage_unit_cost -> amount (captured as the `amount` on USAGE_BASED LicensePeriods)
    - minimum_price -> amount
        from Cycles, we now capture this term via an additional LicensePeriod type: `Type.MINIMUM_COST`
    - incremental_user_price -> amount
        from Cycles, we now capture this term via an additional LicensePeriod type: `Type.INCREMENTAL_USER_COST`

    Args:
        - subscription (models): The Subscription associated with this LicensePeriod. May not be filled,
            as a Contract can also be associated with a Subscription. This is an XOR:
            a Spend Obligation can be associated with a Subscription or a Contract, but not both.
        - type (TextField): The type of obligation. E.g. `Enterprise`, `User Limit`, `Per User`.
        - price (MoneyField): The amount of spend recorded by this LicensePeriod. This field can be localized to any
            currency, with the default being USD. The meaning of `price` changes based on the `type` of the
            LicensePeriod.
            Encapsulates the use case of the following field that was recently removed:
            - minimum_price (MoneyField): The minimum amount of spend required by this LicensePeriod. This field would
                matter if, for instance, a USAGE_BASED subscription costs the greater of $1000 per GB of data used
                or $20000, and the Employer only uses 5GB of data. Similar situations occur for PER_USER subscriptions.
                Only applicable to PER_USER and USAGE_BASED LicensePeriods.
        - calculated_total_price (MoneyField)
        - exchange_rate_to_usd_at_time_of_purchase (DecimalField): Used to compare LicensePeriods that use different
            currencies. USD is used as the comparison currency, but this choice is arbitrary; the comparison currency
            could just as well be Euros, Pounds, etc...
        - start_date (DateField): The date on which this LicensePeriod takes effect
        - end_date (DateField): The date on which this LicensePeriod ends (inclusive)
        - max_credits (PositiveIntegerField): The maximum number of credits provided under this LicensePeriod. Only
            applicable to PREPAID_CREDIT LicensePeriods.
        - max_users (IntegerField): The maximum number of users allowed under this LicensePeriod. Only
            applicable to USER_LIMIT LicensePeriods.
        - incremental_user_price (MoneyField): The price charged for each additional user beyond `max_users`. Only
            applicable to USER_LIMIT LicensePeriods.
        - usage_unit_price (DecimalField): The price per unit for USAGE_BASED LicensePeriods. Only applicable to
            USAGE_BASED LicensePeriods.
        - usage_unit (TextField): The unit of usage for USAGE_BASED LicensePeriods. Only applicable to USAGE_BASED
            LicensePeriods.
    """

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="licenses_periods", null=True)
    type = models.SmallIntegerField(choices=LICENSES_PERIODS_TYPES, default=LICENSE_PERIOD_TYPE_OTHER)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency="USD", default=0)
    calculated_total_price = MoneyField(max_digits=14, decimal_places=2, default_currency="USD", default=0)
    exchange_rate_to_usd_at_time_of_purchase = models.DecimalField(max_digits=14, decimal_places=6)
    # The LicensePeriod's start_date and end_date can capture multi-term contracts but will often be redundant
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    max_credits = models.PositiveIntegerField(null=True, blank=True)
    max_users = models.IntegerField(null=True, blank=True)
    incremental_user_price = MoneyField(max_digits=14, decimal_places=2, default_currency="USD", default=0, null=True)
    usage_unit_price = MoneyField(max_digits=14, decimal_places=2, default_currency="USD", default=0, null=True)
    usage_unit = models.SmallIntegerField(
        choices=LICENSES_PERIODS_USAGE_UNITS, default=LICENSE_PERIOD_USAGE_UNIT_OTHER, null=True, blank=True
    )
    proposal_price = MoneyField(max_digits=14, decimal_places=2, default_currency="USD", null=True)
    proposal_notes = models.TextField(blank=True)

    # Manager
    objects: LicensePeriodManager = LicensePeriodManager()

    class Meta:
        verbose_name_plural = _("Licenses Periods")
        db_table = "licenses_periods"

    def save(self, *args, **kwargs) -> None:
        self.calculated_total_price = self.get_calculated_total_price()
        return super().save(*args, **kwargs)

    def get_status(self) -> str:
        """Returns the status of this LicensePeriod

        WARNING: This method should only be used for LicensePeriod that have been annotated via
        LicensePeriod.objects.annotate(). Due to current deficiencies in django-stubs, we need to
        explicitly cast the product to a WithAnnotations[LicensePeriod] object, meaning that we're
        effectively turning type safety off for this method.

        An AttributeError will be raised if the LicensePeriod has not been annotated with `status`
        """
        # to WithAnnotations. Unfortunately, there is a bug preventing us from doing so at the moment.
        # https://github.com/typeddjango/django-stubs/issues/763
        self_with_annotations = cast(WithAnnotations["LicensePeriod"], self)
        return cast(str, self_with_annotations.status)

    def get_active_employee_license_count(self) -> int:
        """
        Return count of EmployeeLicenses that overlap with dates of license period.
        """
        employee_license_qset = EmployeeLicense.objects.filter(subscription=self.subscription).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=self.start_date)
        )
        if self.end_date:
            employee_license_qset = employee_license_qset.filter(
                Q(start_date__isnull=True) | Q(start_date__lte=self.end_date)
            )
        return employee_license_qset.count()

    @classmethod
    def get_zero_price(cls, currency: Optional[str] = None, decimal_places: Optional[int] = None) -> Money:
        return Money(
            amount=0.0,
            currency=currency or cls._meta.get_field("price").default_currency,
            decimal_places=decimal_places or cls._meta.get_field("price").decimal_places,
        )

    def get_calculated_total_price(self, active_employee_license_count: Optional[int] = None) -> Money:
        """
        If license type is user-limit/per-user, calculate like:
            price + (incrementalUserPrice * max(0, [active_employee_license_count] - maxUsers))
        Else, just return price.

        The LicensePeriod calculated total price will get updated one of these ways:
        - an EmployeeLicense is created with an overlapping date range
        - an EmployeeLicense which had an overlapping date range is deleted
        - an EmployeeLicense is updated to include a LicensePeriod date range
        - an EmployeeLicense is updated to no longer include a LicensePeriod date range
        - (covered by save()) the price field on the LicensePeriod gets updated
        - (covered by save()) the incremental user price field on the LicensePeriod gets updated
        - (covered by save()) the max users field on the LicensePeriod gets updated
        """

        if self.type not in [LICENSE_PERIOD_TYPE_PER_USER, LICENSE_PERIOD_TYPE_USER_LIMIT]:
            return self.price

        zero_amount = self.get_zero_price()
        price = self.price or zero_amount
        incremental_user_price = self.incremental_user_price or zero_amount
        max_users = self.max_users or 0
        user_count = active_employee_license_count or self.get_active_employee_license_count()
        return price + (incremental_user_price * max(0, user_count - max_users))

    def __str__(self) -> str:
        date_string = f"({self.start_date.year}–" + f"{self.end_date.year})" if self.end_date else "present)"
        return f"{self.subscription} {date_string} ({self.price})"
