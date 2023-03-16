from datetime import date, timedelta

import pytest

from api.constants import LICENSE_PERIOD_STATUS_ACTIVE, LICENSE_PERIOD_STATUS_INACTIVE
from api.models import Product
from api.models.Contract import Contract
from api.models.Employee import Employee
from api.models.fixtures import (
    TypeEmployeeFactory,
    TypeEmployeeLicenseFactory,
    TypeLicensePeriodFactory,
    TypeSubscriptionFactory,
)

today = date.today()
tomorrow = today + timedelta(days=1)
long_time_from_now = today + timedelta(weeks=20)
yesterday = today - timedelta(days=1)
long_time_ago = today - timedelta(weeks=100)

employee_email_1 = "btbrbng@concertiv.com"
employee_email_2 = "ctbrbng@concertiv.com"
employee_email_3 = "dtbrbng@concertiv.com"
employee_email_4 = "etbrbng@concertiv.com"


@pytest.mark.django_db
def test_employee_license_end_date_past(
    contract: Contract,
    product: Product,
    employee_factory: TypeEmployeeFactory,
    subscription_factory: TypeSubscriptionFactory,
    employee_license_factory: TypeEmployeeLicenseFactory,
) -> None:
    employee = employee_factory(email=employee_email_1, hire_date=today)
    subscription = subscription_factory(contract, product)
    employee_license = employee_license_factory(employee=employee, subscription=subscription)
    employee_license.end_date = yesterday
    employee_license.save()
    assert today > employee_license.end_date


@pytest.mark.django_db
def test_employee_license_start_and_end_date_equals_today(
    contract: Contract,
    product: Product,
    employee_factory: TypeEmployeeFactory,
    subscription_factory: TypeSubscriptionFactory,
    employee_license_factory: TypeEmployeeLicenseFactory,
) -> None:
    employee = employee_factory(email=employee_email_1, hire_date=today)
    subscription = subscription_factory(contract, product)
    employee_license = employee_license_factory(
        employee=employee, subscription=subscription, start_date=today, end_date=today
    )
    assert employee_license.start_date == employee_license.end_date == today


@pytest.mark.django_db
def test_employee_license_is_in_active_period(
    contract: Contract,
    product: Product,
    employee_factory: TypeEmployeeFactory,
    subscription_factory: TypeSubscriptionFactory,
    employee_license_factory: TypeEmployeeLicenseFactory,
) -> None:
    employee = employee_factory(email=employee_email_1, hire_date=today)
    subscription = subscription_factory(contract, product)
    employee_license = employee_license_factory(
        employee=employee, subscription=subscription, start_date=yesterday, end_date=tomorrow
    )
    assert employee_license.start_date < today < employee_license.end_date


@pytest.mark.django_db
class TestEmployeeLicenseStatusIsActive:
    def test_all_null_dates(
        self,
        contract: Contract,
        product: Product,
        employee: Employee,
        subscription_factory: TypeSubscriptionFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        employee_license = employee_license_factory(
            employee=employee, subscription=subscription, start_date=None, end_date=None
        )
        assert employee_license.get_status() == LICENSE_PERIOD_STATUS_ACTIVE

    def test_null_start_end_inside_subscription_dates(
        self,
        contract: Contract,
        product: Product,
        employee: Employee,
        subscription_factory: TypeSubscriptionFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        license_period_factory(subscription=subscription, start_date=yesterday, end_date=tomorrow)
        employee_license = employee_license_factory(
            employee=employee, subscription=subscription, start_date=None, end_date=None
        )
        assert employee_license.get_status() == LICENSE_PERIOD_STATUS_ACTIVE

    def test_null_start_end_outside_subscription_dates(
        self,
        contract: Contract,
        product: Product,
        employee: Employee,
        subscription_factory: TypeSubscriptionFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        license_period_factory(subscription=subscription, start_date=long_time_ago, end_date=yesterday)
        employee_license = employee_license_factory(
            employee=employee, subscription=subscription, start_date=None, end_date=None
        )
        assert employee_license.subscription.start_date is not None
        assert employee_license.subscription.end_date is not None
        assert employee_license.get_status() == LICENSE_PERIOD_STATUS_INACTIVE

    def test_null_end_valid_start_inside_subscription_dates(
        self,
        contract: Contract,
        product: Product,
        employee: Employee,
        subscription_factory: TypeSubscriptionFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        license_period_factory(subscription=subscription, start_date=yesterday, end_date=tomorrow)
        employee_license = employee_license_factory(
            employee=employee, subscription=subscription, start_date=yesterday, end_date=None
        )
        assert employee_license.get_status() == LICENSE_PERIOD_STATUS_ACTIVE

    def test_null_end_valid_start_outside_subscription_dates(
        self,
        contract: Contract,
        product: Product,
        employee: Employee,
        subscription_factory: TypeSubscriptionFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        license_period_factory(subscription=subscription, start_date=long_time_ago, end_date=yesterday)
        employee_license = employee_license_factory(
            employee=employee, subscription=subscription, start_date=yesterday, end_date=None
        )
        assert employee_license.get_status() == LICENSE_PERIOD_STATUS_INACTIVE

    def test_null_end_invalid_start_inside_subscription_dates(
        self,
        contract: Contract,
        product: Product,
        employee: Employee,
        subscription_factory: TypeSubscriptionFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        license_period_factory(subscription=subscription, start_date=yesterday, end_date=tomorrow)
        employee_license = employee_license_factory(
            employee=employee, subscription=subscription, start_date=tomorrow, end_date=None
        )
        assert employee_license.get_status() == LICENSE_PERIOD_STATUS_INACTIVE

    def test_null_start_invalid_end_inside_subscription_dates(
        self,
        contract: Contract,
        product: Product,
        employee: Employee,
        subscription_factory: TypeSubscriptionFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        license_period_factory(subscription=subscription, start_date=yesterday, end_date=tomorrow)
        employee_license = employee_license_factory(
            employee=employee, subscription=subscription, start_date=None, end_date=yesterday
        )
        assert employee_license.get_status() == LICENSE_PERIOD_STATUS_INACTIVE

    def test_null_start_valid_end_inside_subscription_dates(
        self,
        contract: Contract,
        product: Product,
        employee: Employee,
        subscription_factory: TypeSubscriptionFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        license_period_factory(subscription=subscription, start_date=yesterday, end_date=tomorrow)
        employee_license = employee_license_factory(
            employee=employee, subscription=subscription, start_date=None, end_date=tomorrow
        )
        assert employee_license.get_status() == LICENSE_PERIOD_STATUS_ACTIVE

    def test_null_start_valid_end_outside_subscription_dates(
        self,
        contract: Contract,
        product: Product,
        employee: Employee,
        subscription_factory: TypeSubscriptionFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        license_period_factory(subscription=subscription, start_date=tomorrow, end_date=long_time_from_now)
        employee_license = employee_license_factory(
            employee=employee, subscription=subscription, start_date=None, end_date=tomorrow
        )
        assert employee_license.get_status() == LICENSE_PERIOD_STATUS_INACTIVE

    def test_valid_start_end_inside_subscription_dates(
        self,
        contract: Contract,
        product: Product,
        employee: Employee,
        subscription_factory: TypeSubscriptionFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        license_period_factory(subscription=subscription, start_date=yesterday, end_date=tomorrow)
        employee_license = employee_license_factory(
            employee=employee, subscription=subscription, start_date=yesterday, end_date=tomorrow
        )
        assert employee_license.get_status() == LICENSE_PERIOD_STATUS_ACTIVE

    def test_valid_start_end_before_subscription_start(
        self,
        contract: Contract,
        product: Product,
        employee: Employee,
        subscription_factory: TypeSubscriptionFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        license_period_factory(subscription=subscription, start_date=tomorrow, end_date=long_time_from_now)
        employee_license = employee_license_factory(
            employee=employee, subscription=subscription, start_date=yesterday, end_date=None
        )
        assert employee_license.get_status() == LICENSE_PERIOD_STATUS_INACTIVE

    def test_valid_start_end_after_subscription_end(
        self,
        contract: Contract,
        product: Product,
        employee: Employee,
        subscription_factory: TypeSubscriptionFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        license_period_factory(subscription=subscription, start_date=long_time_ago, end_date=yesterday)
        employee_license = employee_license_factory(
            employee=employee, subscription=subscription, start_date=yesterday, end_date=tomorrow
        )
        assert employee_license.get_status() == LICENSE_PERIOD_STATUS_INACTIVE
