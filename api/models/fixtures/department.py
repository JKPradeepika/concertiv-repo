from typing import Callable

import pytest

from api.models.Department import Department

TypeDepartmentFactory = Callable[..., Department]


@pytest.fixture
def department_factory() -> TypeDepartmentFactory:
    # Closure
    def create_department(name: str = "Research") -> Department:
        return Department.objects.create(name=name)

    return create_department


@pytest.fixture
def department(department_factory: TypeDepartmentFactory) -> Department:
    return department_factory()
