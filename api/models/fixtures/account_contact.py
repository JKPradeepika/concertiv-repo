from typing import Callable

import pytest

from api.constants import ACCOUNT_CONTACT_LABEL_OTHER
from api.models.AccountContact import AccountContact
from api.models.Employer import Employer
from api.models.Person import Person

TypeAccountContactFactory = Callable[..., AccountContact]


@pytest.fixture
def account_contact_factory(employer: Employer, person: Person) -> TypeAccountContactFactory:
    # Closure
    def create_account_contact(
        employer: Employer = employer,
        person: Person = person,
        label: int = ACCOUNT_CONTACT_LABEL_OTHER,
        is_primary: bool = False,
    ) -> AccountContact:
        return AccountContact.objects.create(
            employer=employer,
            person=person,
            label=label,
            is_primary=is_primary,
        )

    return create_account_contact


@pytest.fixture
def account_contact(account_contact_factory: TypeAccountContactFactory) -> AccountContact:
    return account_contact_factory()
