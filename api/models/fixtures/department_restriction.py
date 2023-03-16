from typing import Callable

import pytest

from api.models.DepartmentRestriction import DepartmentRestriction
from api.models.EmployerDepartment import EmployerDepartment
from api.models.Subscription import Subscription

TypeDepartmentRestrictionFactory = Callable[..., DepartmentRestriction]


@pytest.fixture
def department_restriction_factory(
    subscription: Subscription, employer_department: EmployerDepartment
) -> TypeDepartmentRestrictionFactory:
    # Closure
    def create_department_restriction(
        subscription: Subscription = subscription,
        employer_department: EmployerDepartment = employer_department,
    ) -> DepartmentRestriction:
        return DepartmentRestriction.objects.create(
            subscription=subscription,
            employer_department=employer_department,
        )

    return create_department_restriction


@pytest.fixture
def department_restriction(
    department_restriction_factory: TypeDepartmentRestrictionFactory,
) -> DepartmentRestriction:
    return department_restriction_factory()
