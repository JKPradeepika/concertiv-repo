from typing import Callable, Tuple

from django.contrib.auth.models import Group
import pytest

from api.models.Buyer import Buyer
from api.models.Employer import Employer
from api.models.fixtures.buyer import TypeBuyerFactory
from api.models.Supplier import Supplier
from api.models.User import User

TypeUserFactory = Callable[..., User]


@pytest.fixture
def user_factory(buyer: Buyer, group: Group) -> TypeUserFactory:
    # Closure
    def create_user(
        email: str = "aturing@concertiv.com",
        first_name: str = "Alan",
        last_name: str = "Turing",
        password: str = "",
        employer: Employer = buyer.employer,
        is_staff: bool = False,
        is_superuser: bool = True,
        is_active: bool = True,
        groups: Tuple[Group] = (group,),
    ) -> User:
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            employer=employer,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
        )

        if groups:
            user.groups.set(groups)
        return user

    return create_user


@pytest.fixture
def user(user_factory: TypeUserFactory) -> User:
    return user_factory()


@pytest.fixture
def concertiv_user_with_no_permissions(user_factory: TypeUserFactory) -> User:
    return user_factory(email="bituring@concertiv.com", first_name="Blbn", is_superuser=False, groups=None)


@pytest.fixture
def supplier_user_with_no_permissions(user_factory: TypeUserFactory, supplier: Supplier) -> User:
    return user_factory(
        email="situring@concertiv.com", first_name="Blbn", is_superuser=False, groups=None, employer=supplier.employer
    )


@pytest.fixture
def supplier_user(user_factory: TypeUserFactory, supplier: Supplier) -> User:
    return user_factory(
        email="situring@concertiv.com",
        first_name="Slsn",
        groups=None,
        employer=supplier.employer,
    )


@pytest.fixture
def user_with_other_buyer(user_factory: TypeUserFactory, buyer_factory: TypeBuyerFactory) -> User:
    return user_factory(
        email="dituring@concertiv.com",
        first_name="dldn",
        groups=None,
        employer=buyer_factory(name="Other Company", short_code="OC", short_name="OC").employer,
    )
