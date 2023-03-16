from typing import cast

from django.db import models
from django.db.models import Count, Q, QuerySet
from django.db.models.functions import Now, TruncDate
from django.utils.translation import gettext_lazy as _
from django_stubs_ext import WithAnnotations

from api.constants import BUYER_STATUSES, BUYER_STATUS_ACTIVE
from api.mixins import ModelTimeStampMixin
from api.models.BusinessType import BusinessType
from api.models.Contact import Contact
from api.models.Employer import Employer
from api.models.Geography import Geography
from api.models.Industry import Industry
from api.models.Person import Person


class BuyerManager(models.Manager["Buyer"]):
    def get_queryset(self) -> "QuerySet[Buyer]":
        """Annotates each buyer with its active_subscriptions_count"""
        query_set: "QuerySet[Buyer]" = (
            super(BuyerManager, self)
            .get_queryset()
            .annotate(
                active_subscriptions_count=Count(
                    "businessdeal__contracts__subscriptions",
                    filter=Q(businessdeal__contracts__subscriptions__start_date__lte=TruncDate(Now()))
                    & (
                        Q(businessdeal__contracts__subscriptions__end_date__isnull=True)
                        | Q(businessdeal__contracts__subscriptions__end_date__gte=TruncDate(Now()))
                    ),
                )
            )
        )
        return query_set


class Buyer(ModelTimeStampMixin, models.Model):
    """
    A company using the Komodo platform.
    Buyers sit on the buy-side of BusinessDeals.

    Fields dropped from Profiler:
    - user_set_status
    - users_count
    - subscriptions_count
    - logo_url (all entries were null)
    - org_type (all rows are of org_type `member`, except for Concertiv, which is `internal`)
    - primary_contact (moved to AccountContact.primary)

    Fields renamed from Profiler:
    - status -> account_status

    Args:
        - employer (OneToOneField): The employer associated with this buyer.
        - short_name (TextField): A nickname for the buyer (useful if their official name is super long).
            E.g. `Vista`.
        - short_code (TextField): A unique 3-letter identifier for this buyer
        - account_status (TextField): The status of the contract between Concertiv and this employer.
            E.g. `Active`, `Expired`, `Terminated`.
        - savings_report_frequency_in_months (PositiveSmallIntegerField): (DEPRECATED) The frequency with which this
            employer wants us to send them a customer performance report.
        - first_joined_at (DateField): The date on which this buyer joined Concertiv
        - termination_date (DateField): (optional) The date on which this buyer left Concertiv
        - business_type (ForeignKey): (optional) the business type this buyer is related with
    """

    employer = models.OneToOneField(Employer, on_delete=models.CASCADE)
    short_name = models.TextField()
    short_code = models.CharField(unique=True, max_length=5)
    account_status = models.SmallIntegerField(choices=BUYER_STATUSES, default=BUYER_STATUS_ACTIVE)
    savings_report_frequency_in_months = models.PositiveSmallIntegerField(blank=True, null=True)
    first_joined_at = models.DateField()
    termination_date = models.DateField(blank=True, null=True)
    business_type = models.ForeignKey(BusinessType, blank=True, null=True, on_delete=models.SET_NULL)

    # new fields for ManyToMany relation (komodo 420, 493)
    industries = models.ManyToManyField(Industry, db_table="buyer_industries")
    geographies = models.ManyToManyField(Geography, db_table="buyer_geographies")

    # Annotate objects explicitly so that we get better typing support when calling Buyer.objects.*
    objects: models.Manager["Buyer"] = BuyerManager()

    class Meta:
        verbose_name_plural = _("Buyers")
        db_table = "buyers"

    def __str__(self) -> str:
        return self.short_name

    def get_active_subscriptions_count(self) -> int:
        """Returns the number of active subscriptions for this buyer

        WARNING: This method should only be used for buyers that have been annotated via
        Buyer.objects.annotate(). Due to current deficiencies in django-stubs, we need to
        explicitly cast the buyer to a WithAnnotations[Buyer] object, meaning that we're
        effectively turning type safety off for this method.

        An AttributeError will be raised if the buyer has not been annotated with `active_subscriptions_count`
        """
        # TODO We should specify which annotations are valid by adding a second type parameter
        # to WithAnnotations. Unfortunately, there is a bug preventing us from doing so at the moment.
        # https://github.com/typeddjango/django-stubs/issues/763
        self_with_annotations = cast(WithAnnotations["Buyer"], self)
        return cast(int, self_with_annotations.active_subscriptions_count)

    @property
    def contacts(self) -> QuerySet[Contact]:
        persons: models.manager.RelatedManager[Person] = self.employer.persons
        return Contact.objects.filter(person__in=persons.all())
