from typing import Callable

import pytest

from api.models.Department import Department
from api.models.Employer import Employer
from api.models.EmployerDepartment import EmployerDepartment

TypeEmployerDepartmentFactory = Callable[..., EmployerDepartment]


@pytest.fixture
def employer_department_factory(department: Department, employer: Employer) -> TypeEmployerDepartmentFactory:
    # Closure
    def create_employer_department(
        department: Department = department,
        employer: Employer = employer,
        name: str = "Research",
    ) -> EmployerDepartment:
        return EmployerDepartment.objects.create(
            department=department,
            employer=employer,
            name=name,
        )

    return create_employer_department


@pytest.fixture
def employer_department(employer_department_factory: TypeEmployerDepartmentFactory) -> EmployerDepartment:
    return employer_department_factory()
