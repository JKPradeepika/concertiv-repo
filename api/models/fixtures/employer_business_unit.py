from typing import Callable

import pytest

from api.models.Employer import Employer
from api.models.EmployerBusinessUnit import EmployerBusinessUnit

TypeEmployerBusinessUnitFactory = Callable[..., EmployerBusinessUnit]


@pytest.fixture
def employer_business_unit_factory(employer: Employer) -> TypeEmployerBusinessUnitFactory:
    # Closure
    def create_employer_coverage_group(
        employer: Employer = employer,
        name: str = "Employer Business Unit 1",
    ) -> EmployerBusinessUnit:
        return EmployerBusinessUnit.objects.create(
            employer=employer,
            name=name,
        )

    return create_employer_coverage_group


@pytest.fixture
def employer_business_unit(employer_business_unit_factory: TypeEmployerBusinessUnitFactory) -> EmployerBusinessUnit:
    return employer_business_unit_factory()
