from django.core.exceptions import ValidationError
import pytest

from api.models.fixtures import TypePersonFactory
from api.models.Person import Person


@pytest.mark.django_db
def test_full_name_returns_the_first_and_last_name_separated_by_a_space(person: Person) -> None:
    assert person.full_name == "Alan Turing"


@pytest.mark.django_db
def test_full_name_returns_the_first_name_only_when_the_last_name_is_blank(person_factory: TypePersonFactory) -> None:
    person = person_factory(last_name="")
    assert person.full_name == "Alan"


@pytest.mark.django_db
def test_full_name_returns_the_last_name_only_when_the_first_name_is_blank(person_factory: TypePersonFactory) -> None:
    person = person_factory(first_name="")
    assert person.full_name == "Turing"


@pytest.mark.django_db
def test_full_name_returns_a_blank_string_when_first_name_and_last_name_are_blank(
    person_factory: TypePersonFactory,
) -> None:
    person = person_factory(first_name="", last_name="")
    assert person.full_name == ""


@pytest.mark.django_db
def test_person_validates_required_fields(person: Person) -> None:
    with pytest.raises(ValidationError, match=r".*email.*"):
        Person(
            first_name=person.first_name,
            last_name=person.last_name,
            employer=person.employer,
        ).full_clean()

    with pytest.raises(ValidationError, match=r".*first_name.*"):
        Person(
            email=person.email,
            last_name=person.last_name,
            employer=person.employer,
        ).full_clean()

    with pytest.raises(ValidationError, match=r".*last_name.*"):
        Person(
            email=person.email,
            first_name=person.first_name,
            employer=person.employer,
        ).full_clean()
