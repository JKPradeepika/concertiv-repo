from typing import Callable

import pytest

from api.constants import DOMAIN_MARKET_DATA, RESOURCE_ACTION_TERMINATE, RESOURCE_TYPE_USER
from api.models.Employer import Employer
from api.models.Event import Event
from api.models.Person import Person
from api.models.User import User

TypeEventFactory = Callable[..., Event]


@pytest.fixture
def event_factory(employer: Employer, user: User) -> TypeEventFactory:
    # Closure
    def create_event(
        resource_action: int = RESOURCE_ACTION_TERMINATE,
        resource_type: int = RESOURCE_TYPE_USER,
        resource_label: str = "George Boole (gboole@concertiv.com)",
        resource_json: str = "{}",
        notes: str = "George Boole (gboole@concertiv.com) was terminated.",
        source_person_label: str = f"{user.get_first_name()} {user.get_last_name()} ({user.email})",
        source_person: Person = user.person,
        employer: Employer = employer,
        domain: str = DOMAIN_MARKET_DATA,
    ) -> Event:
        return Event.objects.create(
            resource_action=resource_action,
            resource_type=resource_type,
            resource_label=resource_label,
            resource_json=resource_json,
            notes=notes,
            source_person_label=source_person_label,
            source_person=source_person,
            employer=employer,
            domain=domain,
        )

    return create_event


@pytest.fixture
def event(event_factory: TypeEventFactory) -> Event:
    return event_factory()
