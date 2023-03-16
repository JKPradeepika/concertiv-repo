from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from api.mixins import ModelTimeStampMixin
from api.models.Employer import Employer


class Person(ModelTimeStampMixin):
    """
    A baseline record of a person who exists in Komodo. Person records will always be linked to
    one or more Employee, User, or Contact records, which have more specific meanings.

    Args:
        - email (EmailField): The user's email address
        - first_name (TextField): The user's first name
        - last_name (TextField): The user's last name
        - employer (ForeignKey): The user's employer. This is used to authorize requests for employer-specific data.
        - phone_number (PhoneNumberField): (optional) The user's phone number
        - job_title (TextField): (optional) The user's job title. Note that this field differs from the user's
            employee_level. For instance, a user could be at the "Analyst" level, but their job title could be
            "Market Data Analyst."
        - hire_date (DateField): (optional) The date on which this user will start to work for their employer. Future
            dates are allowed. In fact, the primary use of this field is to allow users to add new employees to the
            system before their start date.
        - termination_date (DateField): (optional) The date on which the user stopped or will stop working for their
            employer.
    """

    email = models.EmailField(max_length=254, unique=True, verbose_name="email address")
    first_name = models.TextField()
    last_name = models.TextField()
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name="persons")
    phone_number = PhoneNumberField(null=True, blank=True)
    job_title = models.TextField(null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)  # For scheduling upcoming hires
    termination_date = models.DateField(null=True, blank=True)  # For scheduling upcoming terminations

    class Meta:
        verbose_name_plural = _("Persons")
        db_table = "persons"

    def __str__(self) -> str:
        full_name = self.full_name
        return full_name if full_name else self.email

    @property
    def full_name(self) -> str:
        names_with_blanks_removed = filter(lambda x: x != "", [self.first_name, self.last_name])
        return " ".join(names_with_blanks_removed)

    def clean(self) -> None:
        """Checks that all fields are valid.

        The presence of non-nullable foreign keys is validated by Django,
        so we don't need to check that `employer` is set.

        Raises:
            ValidationError: {"email": "Persons must have an email"}
            ValidationError: {"first_name": "Persons must have a first_name"}
            ValidationError: {"last_name": "Persons must have a last_name"}
        """

        if not self.email:
            raise ValidationError({"email": "Persons must have an email"})
        if not self.first_name:
            raise ValidationError({"first_name": "Persons must have a first_name"})
        if not self.last_name:
            raise ValidationError({"last_name": "Persons must have a last_name"})
