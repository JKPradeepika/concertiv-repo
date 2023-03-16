from typing import Callable

import pytest

from api.models.Employer import Employer
from api.models.EmployerCostCenter import EmployerCostCenter

TypeEmployerCostCenterFactory = Callable[..., EmployerCostCenter]


@pytest.fixture
def employer_cost_center_factory(employer: Employer) -> TypeEmployerCostCenterFactory:
    # Closure
    def create_employer_cost_center(
        employer: Employer = employer,
        name: str = "Human Resources",
    ) -> EmployerCostCenter:
        return EmployerCostCenter.objects.create(
            employer=employer,
            name=name,
        )

    return create_employer_cost_center


@pytest.fixture
def employer_cost_center(employer_cost_center_factory: TypeEmployerCostCenterFactory) -> EmployerCostCenter:
    return employer_cost_center_factory()
