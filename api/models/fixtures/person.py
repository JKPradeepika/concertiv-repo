from datetime import date
from typing import Callable, Optional

import pytest

from api.models.Employer import Employer
from api.models.Person import Person

TypePersonFactory = Callable[..., Person]


@pytest.fixture
def person_factory(employer: Employer) -> TypePersonFactory:
    # Closure
    def create_person(
        email: str = "aturing@concertiv.com",
        first_name: str = "Alan",
        last_name: str = "Turing",
        phone_number: str = "Turing",
        employer: Employer = employer,
        hire_date: Optional[date] = None,
        termination_date: Optional[date] = None,
    ) -> Person:
        return Person.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            employer=employer,
            hire_date=hire_date,
            termination_date=termination_date,
        )

    return create_person


@pytest.fixture
def person(person_factory: TypePersonFactory) -> Person:
    return person_factory()
