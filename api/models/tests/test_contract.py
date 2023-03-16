import pytest

from api.constants import LICENSE_PERIOD_TYPE_PER_USER
from api.models import Product
from api.models.Contract import Contract
from api.models.fixtures import (
    TypeContractFactory,
    TypeEmployeeLicenseFactory,
    TypeLicensePeriodFactory,
    TypeSubscriptionFactory,
)


@pytest.mark.django_db
class TestContractToString:
    def test__str__does_not_specify_dates_if_no_licenses_periods_specified(self, contract: Contract) -> None:
        assert contract.__str__() == f"{contract.business_deal}"

    def test__str__uses_present_instead_of_the_end_date_when_not_specified(
        self,
        contract: Contract,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        license_period = license_period_factory(subscription)
        license_period.end_date = None
        license_period.save()
        assert contract.__str__() == f"{contract.business_deal} ({contract.start_date.year}–present)"

    def test__str__includes_the_end_date_when_specified(
        self,
        contract: Contract,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract, product)
        _ = license_period_factory(subscription)
        assert (
            contract.__str__()
            == f"{contract.business_deal} " + f"({contract.start_date.year}–{contract.end_date.year})"
        )


@pytest.mark.django_db
class TestContractGetDoesAutorenew:
    def test_get_does_autorenew_returns_false_when_the_autorenewal_duration_is_null(
        self,
        contract_factory: TypeContractFactory,
    ) -> None:
        contract = contract_factory(autorenewal_duration=None)
        assert contract.get_does_autorenew() is False

    def test_get_does_autorenew_returns_true_when_the_autorenewal_duration_is_set(
        self,
        contract_factory: TypeContractFactory,
    ) -> None:
        contract = contract_factory(autorenewal_duration=12)
        assert contract.get_does_autorenew() is True


@pytest.mark.django_db
class TestContractCalculatedTotalPrice:
    def test_initial_creation_no_license_periods(self, contract_factory: TypeContractFactory) -> None:
        contract = contract_factory()
        contract.calculated_total_price.amount == 0.0

    def test_initial_creation_one_license_period(
        self,
        contract_factory: TypeContractFactory,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        contract = contract_factory()
        subscription_with_no_lp = subscription_factory(contract=contract)
        subscription_with_lp = subscription_factory(contract=contract)

        contract.refresh_from_db()
        assert contract.calculated_total_price.amount == 0.0

        lp = license_period_factory(subscription=subscription_with_lp)

        contract.refresh_from_db()
        subscription_with_no_lp.refresh_from_db()
        subscription_with_lp.refresh_from_db()

        assert contract.calculated_total_price == lp.calculated_total_price
        assert subscription_with_no_lp.calculated_total_price.amount == 0.0
        assert subscription_with_lp.calculated_total_price == lp.calculated_total_price

    def test_initial_creation_multiple_license_periods(
        self,
        contract_factory: TypeContractFactory,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        contract = contract_factory()
        subscription_with_one_lp = subscription_factory(contract=contract)
        subscription_with_many_lp = subscription_factory(contract=contract)

        license_period_factory(subscription=subscription_with_many_lp)
        license_period_factory(subscription=subscription_with_many_lp)
        lp = license_period_factory(subscription=subscription_with_one_lp)

        contract.refresh_from_db()
        subscription_with_one_lp.refresh_from_db()
        subscription_with_many_lp.refresh_from_db()

        assert contract.calculated_total_price == lp.calculated_total_price * 3
        assert subscription_with_one_lp.calculated_total_price == lp.calculated_total_price
        assert subscription_with_many_lp.calculated_total_price == lp.calculated_total_price * 2

    def test_delete_subscription(
        self,
        contract_factory: TypeContractFactory,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        contract = contract_factory()
        subscription_with_one_lp = subscription_factory(contract=contract)
        subscription_with_many_lp = subscription_factory(contract=contract)

        license_period_factory(subscription=subscription_with_many_lp)
        license_period_factory(subscription=subscription_with_many_lp)
        lp = license_period_factory(subscription=subscription_with_one_lp)

        subscription_with_many_lp.delete()
        contract.refresh_from_db()
        subscription_with_one_lp.refresh_from_db()

        assert contract.calculated_total_price == lp.calculated_total_price
        assert subscription_with_one_lp.calculated_total_price == lp.calculated_total_price

    def test_delete_license_period(
        self,
        contract_factory: TypeContractFactory,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        contract = contract_factory()
        subscription_with_one_lp = subscription_factory(contract=contract)
        subscription_with_many_lp = subscription_factory(contract=contract)

        license_period_factory(subscription=subscription_with_many_lp)
        delete_lp = license_period_factory(subscription=subscription_with_many_lp)
        lp = license_period_factory(subscription=subscription_with_one_lp)

        delete_lp.delete()
        contract.refresh_from_db()
        subscription_with_one_lp.refresh_from_db()
        subscription_with_many_lp.refresh_from_db()

        assert contract.calculated_total_price == lp.calculated_total_price * 2
        assert subscription_with_one_lp.calculated_total_price == lp.calculated_total_price
        assert subscription_with_many_lp.calculated_total_price == lp.calculated_total_price

    def test_update_license_period(
        self,
        contract_factory: TypeContractFactory,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        contract = contract_factory()
        subscription_with_one_lp = subscription_factory(contract=contract)
        subscription_with_many_lp = subscription_factory(contract=contract)

        license_period_factory(subscription=subscription_with_many_lp)
        update_lp = license_period_factory(subscription=subscription_with_many_lp)
        lp = license_period_factory(subscription=subscription_with_one_lp)

        update_lp.price = 0.0
        update_lp.save()

        contract.refresh_from_db()
        subscription_with_one_lp.refresh_from_db()
        subscription_with_many_lp.refresh_from_db()

        assert contract.calculated_total_price == lp.calculated_total_price * 2
        assert subscription_with_one_lp.calculated_total_price == lp.calculated_total_price
        assert subscription_with_many_lp.calculated_total_price == lp.calculated_total_price

    def test_add_employee_license(
        self,
        contract_factory: TypeContractFactory,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
    ) -> None:
        contract = contract_factory()
        subscription_with_one_lp = subscription_factory(contract=contract)
        subscription_with_many_lp = subscription_factory(contract=contract)

        license_period_factory(subscription=subscription_with_many_lp)
        lp = license_period_factory(subscription=subscription_with_many_lp)
        used_lp = license_period_factory(
            subscription=subscription_with_one_lp, type=LICENSE_PERIOD_TYPE_PER_USER, max_users=0
        )

        contract.refresh_from_db()
        subscription_with_one_lp.refresh_from_db()
        subscription_with_many_lp.refresh_from_db()

        assert contract.calculated_total_price == lp.calculated_total_price * 3
        assert subscription_with_one_lp.calculated_total_price == lp.calculated_total_price
        assert subscription_with_many_lp.calculated_total_price == lp.calculated_total_price * 2

        employee_license_factory(
            subscription=subscription_with_one_lp, start_date=used_lp.start_date, end_date=used_lp.end_date
        )

        contract.refresh_from_db()
        subscription_with_one_lp.refresh_from_db()
        subscription_with_many_lp.refresh_from_db()
        used_lp.refresh_from_db()

        assert used_lp.calculated_total_price == used_lp.price + used_lp.incremental_user_price
        assert subscription_with_one_lp.calculated_total_price == used_lp.calculated_total_price
        assert (
            contract.calculated_total_price
            == subscription_with_one_lp.calculated_total_price + subscription_with_many_lp.calculated_total_price
        )

    def test_delete_employee_license(
        self,
        contract_factory: TypeContractFactory,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
    ) -> None:
        contract = contract_factory()
        subscription_with_one_lp = subscription_factory(contract=contract)
        subscription_with_many_lp = subscription_factory(contract=contract)

        license_period_factory(subscription=subscription_with_many_lp)
        lp = license_period_factory(subscription=subscription_with_many_lp)
        used_lp = license_period_factory(
            subscription=subscription_with_one_lp, type=LICENSE_PERIOD_TYPE_PER_USER, max_users=0
        )

        contract.refresh_from_db()
        subscription_with_one_lp.refresh_from_db()
        subscription_with_many_lp.refresh_from_db()

        assert contract.calculated_total_price == lp.calculated_total_price * 3
        assert subscription_with_one_lp.calculated_total_price == lp.calculated_total_price
        assert subscription_with_many_lp.calculated_total_price == lp.calculated_total_price * 2

        el = employee_license_factory(
            subscription=subscription_with_one_lp, start_date=used_lp.start_date, end_date=used_lp.end_date
        )

        contract.refresh_from_db()
        subscription_with_one_lp.refresh_from_db()
        subscription_with_many_lp.refresh_from_db()
        used_lp.refresh_from_db()

        assert used_lp.calculated_total_price == used_lp.price + used_lp.incremental_user_price
        assert subscription_with_one_lp.calculated_total_price == used_lp.calculated_total_price
        assert (
            contract.calculated_total_price
            == subscription_with_one_lp.calculated_total_price + subscription_with_many_lp.calculated_total_price
        )

        el.delete()
        contract.refresh_from_db()
        subscription_with_one_lp.refresh_from_db()
        subscription_with_many_lp.refresh_from_db()
        used_lp.refresh_from_db()

        assert used_lp.calculated_total_price == used_lp.price
        assert subscription_with_one_lp.calculated_total_price == used_lp.calculated_total_price
        assert (
            contract.calculated_total_price
            == subscription_with_one_lp.calculated_total_price + subscription_with_many_lp.calculated_total_price
        )
