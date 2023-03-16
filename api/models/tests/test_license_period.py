from datetime import timedelta
from typing import List

from django.utils import timezone
import pytest

from api.constants import (
    LICENSE_PERIOD_STATUS_ACTIVE,
    LICENSE_PERIOD_STATUS_UPCOMING,
    LICENSE_PERIOD_STATUS_INACTIVE,
    LICENSE_PERIOD_TYPE_ENTERPRISE,
    LICENSE_PERIOD_TYPE_PER_USER,
    LICENSE_PERIOD_TYPE_USER_LIMIT,
)
from api.models.fixtures import (
    TypeEmployeeLicenseFactory,
    TypeLicensePeriodFactory,
    TypeSubscriptionFactory,
)
from api.models.Contract import Contract
from api.models.Product import Product
from api.models.LicensePeriod import LicensePeriod
from api.models.Subscription import Subscription
from api.models.Employee import Employee

three_years_ago = (timezone.now() - timedelta(days=365 * 3)).date()
two_years_ago = (timezone.now() - timedelta(days=365 * 2)).date()
one_year_ago = (timezone.now() - timedelta(days=365)).date()
now = timezone.now().date()
one_year_from_now = (timezone.now() + timedelta(days=365)).date()
two_years_from_now = (timezone.now() + timedelta(days=365 * 2)).date()
three_years_from_now = (timezone.now() + timedelta(days=365 * 3)).date()


@pytest.mark.django_db
class TestLicensePeriodCascadingStartEndDates:
    def test_subscription_and_contract_start_date_update_in_response_to_licenses_periods_being_added(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        license_period_2 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=now, end_date=one_year_from_now
        )

        assert subscription_for_multiple_obligations.start_date == license_period_2.start_date
        assert contract.start_date == license_period_2.start_date

        license_period_1 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=three_years_ago, end_date=two_years_from_now
        )

        assert subscription_for_multiple_obligations.start_date == license_period_1.start_date
        assert contract.start_date == license_period_1.start_date

        _ = license_period_factory(
            subscription=subscription_for_multiple_obligations,
            start_date=two_years_from_now,
            end_date=three_years_from_now,
        )

        assert subscription_for_multiple_obligations.start_date == license_period_1.start_date
        assert contract.start_date == license_period_1.start_date

    def test_subscription_and_contract_end_date_update_in_response_to_licenses_periods_being_added(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        license_period_2 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=now, end_date=now
        )

        assert subscription_for_multiple_obligations.end_date == license_period_2.end_date
        assert contract.end_date == license_period_2.end_date

        license_period_1 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=three_years_ago, end_date=one_year_from_now
        )

        assert subscription_for_multiple_obligations.end_date == license_period_1.end_date
        assert contract.end_date == license_period_1.end_date

        license_period_3 = license_period_factory(
            subscription=subscription_for_multiple_obligations,
            start_date=two_years_from_now,
            end_date=three_years_from_now,
        )

        assert subscription_for_multiple_obligations.end_date == license_period_3.end_date
        assert contract.end_date == license_period_3.end_date

    def test_subscription_and_contract_start_date_update_in_response_to_licenses_periods_being_deleted(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        license_period_1 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=three_years_ago, end_date=two_years_from_now
        )

        license_period_2 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=now, end_date=one_year_from_now
        )

        assert subscription_for_multiple_obligations.start_date == license_period_1.start_date
        assert contract.start_date == license_period_1.start_date

        LicensePeriod.objects.get(pk=license_period_1.pk).delete()

        subscription_for_multiple_obligations = Subscription.objects.get(pk=subscription_for_multiple_obligations.pk)

        assert subscription_for_multiple_obligations.start_date == license_period_2.start_date
        updated_contract = Contract.objects.get(pk=contract.pk)
        assert updated_contract.start_date == license_period_2.start_date

    def test_subscription_and_contract_end_date_update_in_response_to_licenses_periods_being_deleted(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        license_period_1 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=three_years_ago, end_date=two_years_from_now
        )

        license_period_2 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=now, end_date=one_year_from_now
        )

        assert subscription_for_multiple_obligations.end_date == license_period_1.end_date
        assert contract.end_date == license_period_1.end_date

        LicensePeriod.objects.get(pk=license_period_1.pk).delete()

        subscription_for_multiple_obligations = Subscription.objects.get(pk=subscription_for_multiple_obligations.pk)

        assert subscription_for_multiple_obligations.end_date == license_period_2.end_date
        updated_contract = Contract.objects.get(pk=contract.pk)
        assert updated_contract.end_date == license_period_2.end_date

    def test_subscription_and_contract_start_date_update_in_response_to_license_period_start_date_becoming_later(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        license_period_1 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=three_years_ago, end_date=two_years_from_now
        )

        license_period_2 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=now, end_date=one_year_from_now
        )

        license_period_1.start_date = one_year_from_now
        license_period_1.save()

        assert subscription_for_multiple_obligations.start_date == license_period_2.start_date
        assert contract.start_date == license_period_2.start_date

    def test_subscription_and_contract_end_date_update_in_response_to_license_period_end_date_becoming_later(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        _ = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=three_years_ago, end_date=two_years_from_now
        )

        license_period_2 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=now, end_date=one_year_from_now
        )

        license_period_2.end_date = three_years_from_now
        license_period_2.save()

        assert subscription_for_multiple_obligations.end_date == license_period_2.end_date
        assert contract.end_date == license_period_2.end_date

    def test_subscription_and_contract_start_date_update_in_response_to_start_date_becoming_earlier(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        license_period_1 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=two_years_ago, end_date=two_years_from_now
        )
        license_period_1.start_date = three_years_ago
        license_period_1.save()

        assert subscription_for_multiple_obligations.start_date == three_years_ago
        assert contract.start_date == three_years_ago

    def test_subscription_and_contract_end_date_update_in_response_to_license_period_end_date_becoming_earlier(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        license_period_1 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=two_years_ago, end_date=two_years_from_now
        )
        license_period_1.end_date = one_year_from_now
        license_period_1.save()

        assert subscription_for_multiple_obligations.end_date == one_year_from_now
        assert contract.end_date == one_year_from_now

    def test_subscription_and_contract_start_date_update_in_response_to_later_start_date_becoming_earliest(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        _ = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=two_years_ago, end_date=one_year_ago
        )

        license_period_2 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=now, end_date=one_year_from_now
        )

        license_period_2.start_date = three_years_ago
        license_period_2.save()

        assert subscription_for_multiple_obligations.start_date == three_years_ago
        assert contract.start_date == three_years_ago

    def test_subscription_and_contract_end_date_update_in_response_to_earlier_end_date_becoming_latest(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        license_period_1 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=two_years_ago, end_date=one_year_ago
        )

        _ = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=now, end_date=one_year_from_now
        )

        license_period_1.end_date = three_years_from_now
        license_period_1.save()

        assert subscription_for_multiple_obligations.end_date == three_years_from_now
        assert contract.end_date == three_years_from_now

    def test_contract_start_date_updates_when_earliest_license_period_becomes_later_than_other_subscription_(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_one_obligation = subscription_factory(contract, product)
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        _ = license_period_factory(subscription=subscription_for_one_obligation, start_date=two_years_ago, end_date=now)

        license_period_1 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=three_years_ago, end_date=two_years_from_now
        )
        _ = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=now, end_date=one_year_from_now
        )
        _ = license_period_factory(
            subscription=subscription_for_multiple_obligations,
            start_date=two_years_from_now,
            end_date=three_years_from_now,
        )

        assert contract.start_date == license_period_1.start_date

        license_period_1.start_date = one_year_ago
        license_period_1.save()
        assert contract.start_date == two_years_ago

    def test_contract_end_date_updates_when_latest_license_period_becomes_earlier_than_other_subscription(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_one_obligation = subscription_factory(contract, product)
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        _ = license_period_factory(subscription=subscription_for_one_obligation, start_date=two_years_ago, end_date=now)

        _ = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=three_years_ago, end_date=two_years_from_now
        )
        _ = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=now, end_date=one_year_from_now
        )
        license_period_3 = license_period_factory(
            subscription=subscription_for_multiple_obligations,
            start_date=two_years_from_now,
            end_date=three_years_from_now,
        )

        assert contract.end_date == license_period_3.end_date

        license_period_3.end_date = now
        license_period_3.save()
        assert contract.end_date == two_years_from_now

    def test_contract_start_date_updates_when_later_license_period_becomes_earliest(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_one_obligation = subscription_factory(contract, product)
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        license_period_for_singleminded_subscription = license_period_factory(
            subscription=subscription_for_one_obligation, start_date=one_year_ago, end_date=now
        )

        license_period_1 = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=two_years_ago, end_date=two_years_from_now
        )
        _ = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=now, end_date=one_year_from_now
        )
        _ = license_period_factory(
            subscription=subscription_for_multiple_obligations,
            start_date=two_years_from_now,
            end_date=three_years_from_now,
        )

        assert contract.start_date == license_period_1.start_date

        license_period_for_singleminded_subscription.start_date = three_years_ago
        license_period_for_singleminded_subscription.save()
        assert contract.start_date == three_years_ago

    def test_contract_end_date_updates_when_earlier_license_period_becomes_latest(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_one_obligation = subscription_factory(contract, product)
        subscription_for_multiple_obligations = subscription_factory(contract, product)

        license_period_for_singleminded_subscription = license_period_factory(
            subscription=subscription_for_one_obligation, start_date=one_year_ago, end_date=now
        )

        _ = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=two_years_ago, end_date=one_year_from_now
        )
        _ = license_period_factory(
            subscription=subscription_for_multiple_obligations, start_date=now, end_date=one_year_from_now
        )
        license_period_3 = license_period_factory(
            subscription=subscription_for_multiple_obligations,
            start_date=two_years_from_now,
            end_date=two_years_from_now,
        )

        assert contract.end_date == license_period_3.start_date

        license_period_for_singleminded_subscription.end_date = three_years_from_now
        license_period_for_singleminded_subscription.save()
        updated_contract = Contract.objects.get(pk=contract.pk)
        assert updated_contract.end_date == three_years_from_now

    def test_contract_dates_update_on_subscription_delete(
        self,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
        contract: Contract,
    ) -> None:
        subscription_for_one_lp = subscription_factory(contract, product)
        subscription_for_multiple_lps = subscription_factory(contract, product)

        license_period_factory(
            subscription=subscription_for_one_lp, start_date=two_years_ago, end_date=two_years_from_now
        )
        license_period_factory(
            subscription=subscription_for_multiple_lps, start_date=one_year_ago, end_date=one_year_from_now
        )
        license_period_factory(subscription=subscription_for_multiple_lps, start_date=now, end_date=one_year_from_now)

        contract.refresh_from_db()
        assert contract.start_date == two_years_ago
        assert contract.end_date == two_years_from_now

        subscription_for_one_lp.delete()
        contract.refresh_from_db()
        assert contract.start_date == one_year_ago
        assert contract.end_date == one_year_from_now


@pytest.mark.django_db
class TestLicensePeriodStatus:
    def test_status_is_active_when_the_current_date_is_between_the_start_and_end_date_inclusive(
        self,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        now = timezone.now()
        license_period_factory(start_date=now, end_date=now + timedelta(days=365))
        license_period_factory(start_date=now - timedelta(days=365), end_date=now)

        for license_period in LicensePeriod.objects.get_queryset():
            assert license_period.get_status() == LICENSE_PERIOD_STATUS_ACTIVE

    def test_status_is_active_when_the_current_date_is_greater_than_the_start_date_and_the_end_date_is_null(
        self,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        license_period = license_period_factory(start_date=timezone.now(), end_date=None)

        license_period_annotated = LicensePeriod.objects.get_queryset().get(pk=license_period.pk)
        assert license_period_annotated.get_status() == LICENSE_PERIOD_STATUS_ACTIVE

    def test_status_is_upcoming_when_the_current_date_is_less_than_the_start_date(
        self,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        now = timezone.now()
        license_period = license_period_factory(start_date=now + timedelta(days=1), end_date=now + timedelta(366))

        license_period_annotated = LicensePeriod.objects.get_queryset().get(pk=license_period.pk)
        assert license_period_annotated.get_status() == LICENSE_PERIOD_STATUS_UPCOMING

    def test_status_is_inactive_when_the_current_date_is_greater_than_the_end_date(
        self,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        now = timezone.now()
        license_period = license_period_factory(start_date=now - timedelta(days=366), end_date=now - timedelta(1))

        license_period_annotated = LicensePeriod.objects.get_queryset().get(pk=license_period.pk)
        assert license_period_annotated.get_status() == LICENSE_PERIOD_STATUS_INACTIVE

    def test_get_status_throws_an_error_when_the_license_period_is_not_annotated(
        self,
        license_period: LicensePeriod,
    ) -> None:
        with pytest.raises(AttributeError, match=r".*status.*"):
            license_period.get_status()


@pytest.mark.django_db
class TestLicensePeriodCalculatedTotalPrice:
    def create_n_employee_licenses_in_license_period(
        self, employee_license_factory: TypeEmployeeLicenseFactory, employee: Employee, lp: LicensePeriod, n: int
    ) -> List:
        el_list = []
        for _ in range(n):
            el = employee_license_factory(
                employee=employee,
                subscription=lp.subscription,
                start_date=lp.start_date,
                end_date=lp.end_date,
            )
            el_list.append(el)
        return el_list

    @pytest.mark.parametrize("lp_type", [LICENSE_PERIOD_TYPE_PER_USER, LICENSE_PERIOD_TYPE_USER_LIMIT])
    def test_no_employee_license_period(self, lp_type: int, license_period_factory: TypeLicensePeriodFactory) -> None:
        lp = license_period_factory(type=lp_type)
        assert lp.price == lp.calculated_total_price

    @pytest.mark.parametrize("lp_type", [LICENSE_PERIOD_TYPE_PER_USER, LICENSE_PERIOD_TYPE_USER_LIMIT])
    def test_one_employee_license_period(
        self,
        lp_type: int,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        employee: Employee,
        subscription: Subscription,
    ) -> None:
        lp = license_period_factory(type=lp_type, subscription=subscription)
        self.create_n_employee_licenses_in_license_period(employee_license_factory, employee, lp, 1)
        assert lp.price == lp.calculated_total_price

    @pytest.mark.parametrize("lp_type", [LICENSE_PERIOD_TYPE_PER_USER, LICENSE_PERIOD_TYPE_USER_LIMIT])
    def test_create_employee_license(
        self,
        lp_type: int,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        employee: Employee,
        subscription: Subscription,
    ) -> None:
        lp = license_period_factory(type=lp_type, subscription=subscription, max_users=1)
        self.create_n_employee_licenses_in_license_period(employee_license_factory, employee, lp, 2)
        lp.refresh_from_db()
        assert lp.get_calculated_total_price() == lp.calculated_total_price
        assert lp.price < lp.calculated_total_price
        assert lp.calculated_total_price == lp.price * 2

    @pytest.mark.parametrize("lp_type", [LICENSE_PERIOD_TYPE_PER_USER, LICENSE_PERIOD_TYPE_USER_LIMIT])
    def test_delete_employee_license(
        self,
        lp_type: int,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        employee: Employee,
        subscription: Subscription,
    ) -> None:
        lp = license_period_factory(type=lp_type, subscription=subscription, max_users=1)
        el_list = self.create_n_employee_licenses_in_license_period(employee_license_factory, employee, lp, 2)
        el_list[-1].delete()
        lp.refresh_from_db()
        assert lp.get_calculated_total_price() == lp.calculated_total_price
        assert lp.price == lp.calculated_total_price

    @pytest.mark.parametrize("lp_type", [LICENSE_PERIOD_TYPE_PER_USER, LICENSE_PERIOD_TYPE_USER_LIMIT])
    def test_update_employee_license_date_range(
        self,
        lp_type: int,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        employee: Employee,
        subscription: Subscription,
    ) -> None:
        lp = license_period_factory(type=lp_type, subscription=subscription, max_users=1)
        other_lp = license_period_factory(
            type=lp_type,
            subscription=subscription,
            max_users=0,
            start_date=lp.end_date + timedelta(days=1),
            end_date=lp.end_date + timedelta(days=2),
        )
        el_list = self.create_n_employee_licenses_in_license_period(employee_license_factory, employee, lp, 2)

        lp.refresh_from_db()
        other_lp.refresh_from_db()
        assert lp.calculated_total_price > lp.price
        assert other_lp.calculated_total_price == other_lp.price

        updated_el = el_list[-1]
        updated_el.start_date = other_lp.start_date
        updated_el.end_date = other_lp.end_date + timedelta(days=1)
        updated_el.save()

        lp.refresh_from_db()
        other_lp.refresh_from_db()
        assert lp.get_calculated_total_price() == lp.calculated_total_price
        assert other_lp.get_calculated_total_price() == other_lp.calculated_total_price
        assert lp.price == lp.calculated_total_price
        assert other_lp.calculated_total_price > other_lp.price

    def test_update_license_period_type_to_per_user(
        self,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        employee: Employee,
        subscription: Subscription,
    ) -> None:
        lp = license_period_factory(subscription=subscription, max_users=1)
        self.create_n_employee_licenses_in_license_period(employee_license_factory, employee, lp, 2)

        lp.refresh_from_db()
        assert lp.calculated_total_price == lp.price

        lp.type = LICENSE_PERIOD_TYPE_PER_USER
        lp.save()

        lp.refresh_from_db()
        assert lp.calculated_total_price > lp.price

    def test_update_license_period_type_to_user_limit(
        self,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        employee: Employee,
        subscription: Subscription,
    ) -> None:
        lp = license_period_factory(subscription=subscription, max_users=1)
        self.create_n_employee_licenses_in_license_period(employee_license_factory, employee, lp, 2)

        lp.refresh_from_db()
        assert lp.calculated_total_price == lp.price

        lp.type = LICENSE_PERIOD_TYPE_USER_LIMIT
        lp.save()

        lp.refresh_from_db()
        assert lp.calculated_total_price > lp.price

    def test_update_license_period_type_to_enterprise(
        self,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        employee: Employee,
        subscription: Subscription,
    ) -> None:
        lp = license_period_factory(type=LICENSE_PERIOD_TYPE_PER_USER, subscription=subscription, max_users=1)
        self.create_n_employee_licenses_in_license_period(employee_license_factory, employee, lp, 2)

        lp.refresh_from_db()
        assert lp.calculated_total_price > lp.price

        lp.type = LICENSE_PERIOD_TYPE_ENTERPRISE
        lp.save()

        lp.refresh_from_db()
        assert lp.calculated_total_price == lp.price

    @pytest.mark.parametrize("lp_type", [LICENSE_PERIOD_TYPE_PER_USER, LICENSE_PERIOD_TYPE_USER_LIMIT])
    def test_update_license_period_price(
        self,
        lp_type: int,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        employee: Employee,
        subscription: Subscription,
    ) -> None:
        lp = license_period_factory(type=lp_type, subscription=subscription, max_users=1)
        self.create_n_employee_licenses_in_license_period(employee_license_factory, employee, lp, 2)
        lp.refresh_from_db()
        assert lp.get_calculated_total_price() == lp.calculated_total_price
        assert lp.price < lp.calculated_total_price
        assert lp.calculated_total_price == lp.price + lp.incremental_user_price

        lp.price = 1.0
        lp.save()
        assert lp.get_calculated_total_price() == lp.calculated_total_price
        assert lp.price < lp.calculated_total_price
        assert lp.calculated_total_price == lp.price + lp.incremental_user_price

    @pytest.mark.parametrize("lp_type", [LICENSE_PERIOD_TYPE_PER_USER, LICENSE_PERIOD_TYPE_USER_LIMIT])
    def test_update_license_period_max_users(
        self,
        lp_type: int,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        employee: Employee,
        subscription: Subscription,
    ) -> None:
        lp = license_period_factory(type=lp_type, subscription=subscription, max_users=1)
        self.create_n_employee_licenses_in_license_period(employee_license_factory, employee, lp, 2)
        lp.refresh_from_db()
        assert lp.get_calculated_total_price() == lp.calculated_total_price
        assert lp.price < lp.calculated_total_price
        assert lp.calculated_total_price == lp.price + lp.incremental_user_price

        lp.max_users = 2
        lp.save()
        assert lp.get_calculated_total_price() == lp.calculated_total_price
        assert lp.price == lp.calculated_total_price

    @pytest.mark.parametrize("lp_type", [LICENSE_PERIOD_TYPE_PER_USER, LICENSE_PERIOD_TYPE_USER_LIMIT])
    def test_update_license_period_incremental_user_price(
        self,
        lp_type: int,
        license_period_factory: TypeLicensePeriodFactory,
        employee_license_factory: TypeEmployeeLicenseFactory,
        employee: Employee,
        subscription: Subscription,
    ) -> None:
        lp = license_period_factory(type=lp_type, subscription=subscription, max_users=1)
        self.create_n_employee_licenses_in_license_period(employee_license_factory, employee, lp, 2)
        lp.refresh_from_db()
        assert lp.get_calculated_total_price() == lp.calculated_total_price
        assert lp.price < lp.calculated_total_price
        assert lp.calculated_total_price == lp.price + lp.incremental_user_price

        lp.incremental_user_price = 2.0
        lp.save()
        assert lp.get_calculated_total_price() == lp.calculated_total_price
        assert lp.calculated_total_price == lp.price + lp.incremental_user_price
