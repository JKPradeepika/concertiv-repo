from typing import Callable, Optional

import pytest

from api.models.Employer import Employer
from api.models.EmployerGeography import EmployerGeography
from api.models.Geography import Geography

TypeEmployerGeographyFactory = Callable[..., EmployerGeography]


@pytest.fixture
def employer_geography_factory(
    geography: Geography, employer: Employer, name: str = "CEO"
) -> TypeEmployerGeographyFactory:
    # Closure
    def create_employer_geography(
        geography: Geography = geography,
        employer: Employer = employer,
        name: str = name,
        parent: Optional[EmployerGeography] = None,
    ) -> EmployerGeography:
        return EmployerGeography.objects.create(
            geography=geography,
            employer=employer,
            name=name,
            parent=parent,
        )

    return create_employer_geography


@pytest.fixture
def employer_geography(employer_geography_factory: TypeEmployerGeographyFactory) -> EmployerGeography:
    return employer_geography_factory()
