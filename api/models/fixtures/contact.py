from typing import Any, Callable, Dict

import pytest

from api.models.Contact import Contact
from api.models.Employer import Employer
from api.models.fixtures.person import TypePersonFactory
from api.models.Person import Person

TypeContactFactory = Callable[..., Contact]


@pytest.fixture
def contact_factory(person_factory: TypePersonFactory, employer: Employer) -> TypeContactFactory:

    # Closure
    def create_contact(
        email: str = "aturing@concertiv.com",
        first_name: str = "Alan",
        last_name: str = "Turing",
        phone_number: str = "+12345678910",
        description: str = "Head of Computers",
        is_primary: bool = True,
        employer: Employer = employer,
        **kwargs: Dict[str, Any],
    ) -> Contact:
        person: Person = person_factory(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            employer=employer,
        )
        contact: Contact = Contact.objects.create(
            person=person,
            description=description,
            is_primary=is_primary,
        )
        return contact

    return create_contact


@pytest.fixture
def contact(contact_factory: TypeContactFactory) -> Contact:
    return contact_factory()
