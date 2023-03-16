from datetime import date
from typing import Callable, Optional

import pytest

from api.models.Employee import Employee
from api.models.Subscription import Subscription
from api.models.EmployeeLicense import EmployeeLicense

TypeEmployeeLicenseFactory = Callable[..., EmployeeLicense]


@pytest.fixture
def employee_license_factory(employee: Employee, subscription: Subscription) -> TypeEmployeeLicenseFactory:
    def create_employee_license(
        employee: Employee = employee,
        subscription: Subscription = subscription,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> EmployeeLicense:
        return EmployeeLicense.objects.create(
            employee=employee, subscription=subscription, start_date=start_date, end_date=end_date
        )

    return create_employee_license


@pytest.fixture
def employee_license(employee_license_factory: TypeEmployeeLicenseFactory) -> EmployeeLicense:
    return employee_license_factory()
