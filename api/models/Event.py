from django.db import models
from django.utils.translation import gettext_lazy as _

from api.constants import DOMAINS, RESOURCES_ACTIONS, RESOURCES_TYPES
from api.mixins import ModelTimeStampMixin
from api.models.Employer import Employer
from api.models.Person import Person


class Event(ModelTimeStampMixin, models.Model):
    """
    A record of a create, update, or delete event that took place within Profiler or Komodo.
    Events are used by account managers for auditing purposes.
    E.g. Account managers can use Events to check whether or not a license was deprovisioned & if it was, the data on
    which it was deprovisioned.

    Fields dropped from Profiler:
    - user_label
    - user

    Fields renamed from Profiler:
    - admin_label -> source_person_label
    - admin -> source_person

    Args:
        resource_action (Int): The type of action taken. E.g. `Add`, `Change`, `Remove`, `Terminate`, `Activate`.
        resource_type (TextField): The type of resource acted upon. E.g. `Subscription`, `License`, `User`.
        resource_label (TextField): A label used to identify the affected resource. Application components should use
            meaningful labels when creating events. E.g. For a product, use `Product.name (Supplier.name)`.
        resource_json (JSONField): A snapshot of the resource, taken just after it has been created / updated, or just
            before it has been removed
        notes (TextField): A human-readable summary of the event. E.g. "Price for WSJ Pro Private Equity changed from
            $3477.60 to $3149.50"
        source_person_label (TextField): A string containing the name and email address of the person who triggered this
            event (generated at the time the event occurred). E.g. `Jeff Terry (jeff.terry@concertiv.com)`.
        source_person (ForeignKey): The person who triggered this event
        employer (ForeignKey): The employer whose data was affected by this event
        domain (TextField): The domain to which the data affected this event belongs
    """

    resource_action = models.SmallIntegerField(choices=RESOURCES_ACTIONS)
    resource_type = models.SmallIntegerField(choices=RESOURCES_TYPES)
    resource_label = models.TextField()
    resource_json = models.JSONField()
    notes = models.TextField()
    source_person_label = models.TextField(blank=True, null=True)
    source_person = models.ForeignKey(
        Person, related_name="source_person_event", on_delete=models.PROTECT, null=True, blank=True
    )
    employer = models.ForeignKey(Employer, on_delete=models.PROTECT)
    domain = models.SmallIntegerField(choices=DOMAINS, blank=True, null=True)

    class Meta:
        verbose_name_plural = _("Events")
        db_table = "events"

    def __str__(self) -> str:
        return f"{self.resource_action} {self.resource_type}: {self.resource_label}"
