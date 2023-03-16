from typing import Callable

import pytest

from api.models.Address import Address

TypeAddressFactory = Callable[..., Address]


@pytest.fixture
def address_factory() -> TypeAddressFactory:
    # Closure
    def create_address(
        street1: str = "1600 Pennsylvania Ave.",
        street2: str = "",
        city: str = "Washington",
        state: str = "DC",
        country: str = "United States",
        postal_code: str = "205000",
        is_primary: bool = True,
    ) -> Address:
        return Address.objects.create(
            street1=street1,
            street2=street2,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
            is_primary=is_primary,
        )

    return create_address


@pytest.fixture
def address(address_factory: TypeAddressFactory) -> Address:
    return address_factory()
