from django.db import models
from django.utils.translation import gettext_lazy as _

from api.constants import ACCOUNT_CONTACT_LABEL_AM_400_MARKET_DATA, ACCOUNT_CONTACT_LABELS
from api.mixins import ModelTimeStampMixin
from api.models.Employer import Employer
from api.models.Person import Person


class AccountContact(ModelTimeStampMixin, models.Model):
    """
    The Concertiv account manager in charge of part of an Employer's account.
    AccountContacts can either be in charge of managing a specific domain, or they can be in charge of the managing the
    overall client account.

    Fields whose type changed from Profiler:
    - primary (moved from an fk on Employer to a boolean on AccountContact)

    Args:
        - employer (ForeignKey): The employer for whom this person is a contact
        - person (ForeignKey): The contact (i.e. the Concertiv account manager in charge of the associated employer)
        - label (TextField): The type of contact. E.g. `Market Data Contact`, `Technology Contact`,
            `Senior Account Contact`
        - is_primary (BooleanField): Whether this contact is the primary contact for this employer. Only one contact
            should be listed as the primary contact.
    """

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    label = models.SmallIntegerField(choices=ACCOUNT_CONTACT_LABELS, default=ACCOUNT_CONTACT_LABEL_AM_400_MARKET_DATA)
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = _("Account Contacts")
        db_table = "accounts_contacts"

    def __str__(self) -> str:
        return str(self.person)
