from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.Address import Address
from api.models.Industry import Industry


class Employer(ModelTimeStampMixin, models.Model):
    """
    A company using the Komodo platform.
    Employers sit on the buy-side of BusinessDeals.

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
        - name (TextField): The name of the employer. E.g. `Vista Equity Partners Management, LLC`.
        - address (ManyToManyField): One or more addresses associated with this employer
        - industries (ManyToManyField): One or more industries in which this employer works.
            E.g. `Private Equity`, `Investment Bank`.
        - profiler_id (Integer): Temporary field to store the original id in Profiler (for data migration)
    """

    name = models.TextField()
    addresses = models.ManyToManyField(Address, db_table="employers_addresses")
    industries = models.ManyToManyField(Industry, db_table="employers_industries")
    profiler_id = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = _("Employers")
        db_table = "employers"

    def __str__(self) -> str:
        return self.name
