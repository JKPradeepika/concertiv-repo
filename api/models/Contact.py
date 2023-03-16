from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.Person import Person


# TODO: Maybe this model will be deleted because the new models for SupplierContact and BuyerContact
class Contact(ModelTimeStampMixin, models.Model):
    """
    A contact at an Employer or a contact at a Supplier who manages subscriptions to a specific Product.

    Fields renamed from Profiler:
    - contactable_type -> replaced by the EmployerContact and ProductContact tables
    - contactable_id -> replaced by the EmployerContact and ProductContact tables
    - phone -> phone_number
    - title -> description

    Args:
        - person (Person): The contact's person fk object related with
        - description (TextField): A couple of words describing this Contact. Often a job title.
    """

    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    description = models.TextField(blank=True)  # What's this field for ? ? ?
    is_primary = models.BooleanField(default=False)  # What's this field for ? ? ?

    class Meta:
        verbose_name_plural = _("Contacts")
        db_table = "contacts"

    def __str__(self) -> str:
        return str(self.person)
