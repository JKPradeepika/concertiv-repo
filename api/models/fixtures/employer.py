from typing import Callable

import pytest

from api.models.Employer import Employer

TypeEmployerFactory = Callable[..., Employer]


@pytest.fixture
def employer_factory() -> TypeEmployerFactory:
    # Closure
    def create_employer(name: str = "Concertiv, Inc.") -> Employer:
        return Employer.objects.create(name=name)

    return create_employer


@pytest.fixture
def employer(employer_factory: TypeEmployerFactory) -> Employer:
    return employer_factory()


@pytest.fixture
def supplier_employer(employer_factory: TypeEmployerFactory) -> Employer:
    return employer_factory(name="Cheesy Puff Factory")
