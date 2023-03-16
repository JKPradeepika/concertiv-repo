from typing import Callable

import pytest

from api.models.EmployeeLevel import EmployeeLevel
from api.models.Employer import Employer
from api.models.EmployerEmployeeLevel import EmployerEmployeeLevel

TypeEmployerEmployeeLevelFactory = Callable[..., EmployerEmployeeLevel]


@pytest.fixture
def employer_employee_level_factory(
    employee_level: EmployeeLevel, employer: Employer
) -> TypeEmployerEmployeeLevelFactory:
    # Closure
    def create_employer_employee_level(
        employee_level: EmployeeLevel = employee_level,
        employer: Employer = employer,
        name: str = "CEO",
    ) -> EmployerEmployeeLevel:
        return EmployerEmployeeLevel.objects.create(
            employee_level=employee_level,
            employer=employer,
            name=name,
        )

    return create_employer_employee_level


@pytest.fixture
def employer_employee_level(employer_employee_level_factory: TypeEmployerEmployeeLevelFactory) -> EmployerEmployeeLevel:
    return employer_employee_level_factory()
