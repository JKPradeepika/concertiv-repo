from typing import Callable

import pytest

from api.models.EmployeeLevel import EmployeeLevel

TypeEmployeeLevelFactory = Callable[..., EmployeeLevel]


@pytest.fixture
def employee_level_factory() -> TypeEmployeeLevelFactory:
    # Closure
    def create_employee_level(name: str = "CEO") -> EmployeeLevel:
        return EmployeeLevel.objects.create(name=name)

    return create_employee_level


@pytest.fixture
def employee_level(employee_level_factory: TypeEmployeeLevelFactory) -> EmployeeLevel:
    return employee_level_factory()
