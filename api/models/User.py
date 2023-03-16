from typing import Optional, Union
from uuid import UUID

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.Employer import Employer
from api.models.Person import Person

UserFieldTypes = Union[str, int, bool, UUID, Employer]


class UserManager(BaseUserManager["User"]):
    """
    Custom user model manager where emails are the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        employer: Employer,
        password: Optional[str] = None,
        **extra_fields: UserFieldTypes
    ) -> "User":
        """
        Create and save a User with the given email, first_name, last_name, and employer
        """
        email = self.normalize_email(email).lower()

        with transaction.atomic():
            person, _ = Person.objects.update_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "employer": employer,
                },
            )

            user: "User" = self.model(
                email=email,
                person=person,
                **extra_fields,
            )

            # Users shouldn't usually have passwords, but the user model currently requires
            # a password, so we set an unusable one.
            if password:
                user.set_password(password)
            else:
                user.set_unusable_password()

            user.full_clean()
            user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email: str,
        password: str,
        first_name: str = "Django",
        last_name: str = "Superuser",
        employer: Optional[Employer] = None,
        **extra_fields: UserFieldTypes
    ) -> "User":
        """
        Create and save a superuser with the given email and password.
        """

        # Set the employer to Concertiv by default
        if not employer:
            employer, _ = Employer.objects.get_or_create(
                name="Concertiv, Inc.",
                defaults={"name": "Concertiv, Inc."},
            )

        # Concertiv users group
        group, _ = Group.objects.get_or_create(name="concertiv")

        # Create User
        user = self.create_user(email, first_name, last_name, employer, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.groups.add(group)  # add user to Concertiv Group required for endpoint policies permissions
        user.save(using=self._db)
        return user


class User(ModelTimeStampMixin, PermissionsMixin, AbstractBaseUser):
    """
    A user who is authorized to log in. The User model is used by Django's authentication
    and authorization systems.

    Args:
        - person (Person): The person associated with this user, which contains their email address, name, etc...
    """

    email = models.EmailField(max_length=254, unique=True, verbose_name="email address")
    person = models.OneToOneField(Person, on_delete=models.CASCADE)

    # Default Django fields
    is_staff = models.BooleanField(
        verbose_name=_("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        verbose_name=_("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
        ),
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    class Meta:
        verbose_name_plural = _("Users")
        db_table = "users"

    def __str__(self) -> str:
        return self.person.__str__()

    def get_first_name(self) -> str:
        return self.person.first_name

    def get_last_name(self) -> str:
        return self.person.last_name

    def get_employer(self) -> Employer:
        return self.person.employer
