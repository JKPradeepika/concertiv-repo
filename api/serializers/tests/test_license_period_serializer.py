from datetime import timedelta

import pytest

from api.models.fixtures import (
    TypeEmployeeLicenseFactory,
    TypeLicensePeriodFactory,
    TypeSubscriptionFactory,
)
from api.models.Contract import Contract
from api.models.Employee import Employee
from api.models.Product import Product
from api.serializers.LicensePeriodSerializer import LicensePeriodSerializer


@pytest.mark.django_db
class TestGetActiveEmployeeLicenseCount:
    def test_no_employee_licenses_zero(
        self,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
        product: Product,
    ) -> None:
        subscription = subscription_factory(contract, product)
        lp = license_period_factory(subscription=subscription)
        assert LicensePeriodSerializer.get_active_employee_license_count(lp) == 0

    def test_null_el_start_end_one(
        self,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        contract: Contract,
        employee: Employee,
        product: Product,
    ) -> None:
        subscription = subscription_factory(contract, product)
        lp = license_period_factory(subscription=subscription)
        employee_license_factory(subscription=subscription, employee=employee)
        assert LicensePeriodSerializer.get_active_employee_license_count(lp) == 1

    def test_el_end_before_license_start_zero(
        self,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        contract: Contract,
        employee: Employee,
        product: Product,
    ) -> None:
        subscription = subscription_factory(contract, product)
        lp = license_period_factory(subscription=subscription)
        employee_license_factory(
            subscription=subscription, employee=employee, end_date=lp.start_date - timedelta(days=1)
        )
        assert LicensePeriodSerializer.get_active_employee_license_count(lp) == 0

    def test_el_end_after_license_start_one(
        self,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        contract: Contract,
        employee: Employee,
        product: Product,
    ) -> None:
        subscription = subscription_factory(contract, product)
        lp = license_period_factory(subscription=subscription)
        employee_license_factory(
            subscription=subscription, employee=employee, end_date=lp.start_date + timedelta(days=1)
        )
        assert LicensePeriodSerializer.get_active_employee_license_count(lp) == 1

    def test_el_start_before_license_start_one(
        self,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        contract: Contract,
        employee: Employee,
        product: Product,
    ) -> None:
        subscription = subscription_factory(contract, product)
        lp = license_period_factory(subscription=subscription)
        employee_license_factory(
            subscription=subscription, employee=employee, start_date=lp.start_date - timedelta(days=1)
        )
        assert LicensePeriodSerializer.get_active_employee_license_count(lp) == 1

    def test_el_start_before_end_before_license_start_zero(
        self,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        contract: Contract,
        employee: Employee,
        product: Product,
    ) -> None:
        subscription = subscription_factory(contract, product)
        lp = license_period_factory(subscription=subscription)
        employee_license_factory(
            subscription=subscription,
            employee=employee,
            start_date=lp.start_date - timedelta(days=2),
            end_date=lp.start_date - timedelta(days=1),
        )
        assert LicensePeriodSerializer.get_active_employee_license_count(lp) == 0

    def test_el_start_before_end_after_license_start_one(
        self,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        contract: Contract,
        employee: Employee,
        product: Product,
    ) -> None:
        subscription = subscription_factory(contract, product)
        lp = license_period_factory(subscription=subscription)
        employee_license_factory(
            subscription=subscription,
            employee=employee,
            start_date=lp.start_date - timedelta(days=1),
            end_date=lp.start_date + timedelta(days=1),
        )
        assert LicensePeriodSerializer.get_active_employee_license_count(lp) == 1

    def test_el_start_after_end_after_license_start_one(
        self,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        contract: Contract,
        employee: Employee,
        product: Product,
    ) -> None:
        subscription = subscription_factory(contract, product)
        lp = license_period_factory(subscription=subscription)
        employee_license_factory(
            subscription=subscription,
            employee=employee,
            start_date=lp.start_date + timedelta(days=1),
            end_date=lp.start_date + timedelta(days=2),
        )
        assert LicensePeriodSerializer.get_active_employee_license_count(lp) == 1

    def test_el_start_after_license_end_zero(
        self,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        contract: Contract,
        employee: Employee,
        product: Product,
    ) -> None:
        subscription = subscription_factory(contract, product)
        lp = license_period_factory(subscription=subscription)
        employee_license_factory(
            subscription=subscription, employee=employee, start_date=lp.end_date + timedelta(days=1)
        )
        assert LicensePeriodSerializer.get_active_employee_license_count(lp) == 0

    def test_el_start_after_end_after_license_end_zero(
        self,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        contract: Contract,
        employee: Employee,
        product: Product,
    ) -> None:
        subscription = subscription_factory(contract, product)
        lp = license_period_factory(subscription=subscription)
        employee_license_factory(
            subscription=subscription,
            employee=employee,
            start_date=lp.end_date + timedelta(days=1),
            end_date=lp.end_date + timedelta(days=2),
        )
        assert LicensePeriodSerializer.get_active_employee_license_count(lp) == 0
