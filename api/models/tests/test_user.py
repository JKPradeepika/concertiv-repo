import pytest

from api.models.Employer import Employer
from api.models.fixtures import TypeEmployerFactory
from api.models.Person import Person
from api.models.User import User


@pytest.mark.django_db
def test_create_user_creates_a_new_user(employer: Employer) -> None:
    user: User = User.objects.create_user(
        email="gboole@concertiv.com",
        first_name="George",
        last_name="Boole",
        employer=employer,
    )

    assert user.id is not None
    assert user.email == "gboole@concertiv.com"
    assert user.get_first_name() == "George"
    assert user.get_last_name() == "Boole"
    assert user.get_employer().id == employer.id


@pytest.mark.django_db
def test_create_user_associates_the_new_user_with_an_existing_person_when_possible(person: Person) -> None:
    user: User = User.objects.create_user(
        email=person.email,
        first_name=person.first_name,
        last_name=person.last_name,
        employer=person.employer,
    )

    assert user.id is not None
    assert user.email == person.email
    assert user.get_first_name() == person.first_name
    assert user.get_last_name() == person.last_name
    assert user.get_employer().id == person.employer.id


@pytest.mark.django_db
def test_create_user_updates_the_associated_person(person: Person, employer_factory: TypeEmployerFactory) -> None:
    new_employer = employer_factory(name="NewEmployer")
    user: User = User.objects.create_user(
        email=person.email,
        first_name="NewFirstName",
        last_name="NewLastName",
        employer=new_employer,
    )

    assert user.id is not None
    assert user.email == person.email
    assert user.get_first_name() == "NewFirstName"
    assert user.get_last_name() == "NewLastName"
    assert user.get_employer().id == new_employer.id


@pytest.mark.django_db
def test_create_user_can_set_a_password(employer: Employer) -> None:
    user: User = User.objects.create_user(
        email="gboole@concertiv.com",
        first_name="George",
        last_name="Boole",
        employer=employer,
        password="GreatPassword35!",
    )

    assert user.check_password("GreatPassword35!") is True


@pytest.mark.django_db
def test_create_user_lowercases_the_email_address(employer: Employer) -> None:
    user: User = User.objects.create_user(
        email="GBOOLE@CONCERTIV.COM",
        first_name="George",
        last_name="Boole",
        employer=employer,
    )

    assert user.email == "gboole@concertiv.com"


@pytest.mark.django_db
def test_create_superuser_creates_a_new_superuser(employer: Employer) -> None:
    superuser: User = User.objects.create_superuser(
        email="gboole@concertiv.com",
        first_name="George",
        last_name="Boole",
        password="GreatPassword35!",
        employer=employer,
    )

    assert superuser.id is not None
    assert superuser.email == "gboole@concertiv.com"
    assert superuser.get_first_name() == "George"
    assert superuser.get_last_name() == "Boole"
    assert superuser.get_employer().id == employer.id
    assert superuser.check_password("GreatPassword35!") is True


@pytest.mark.django_db
def test_create_superuser_sets_the_employer_to_concertiv_by_default() -> None:
    superuser: User = User.objects.create_superuser(
        email="gboole@concertiv.com",
        first_name="George",
        last_name="Boole",
        password="GreatPassword35!",
    )

    assert superuser.get_employer() is not None
    assert superuser.get_employer().name == "Concertiv, Inc."
