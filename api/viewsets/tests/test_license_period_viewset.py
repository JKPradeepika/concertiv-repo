import pytest
from rest_framework import status

from api.constants import DOMAIN_INSURANCE, DOMAINS
from api.models import Contract, LicensePeriod, Product, User
from api.models.fixtures import (
    TypeBusinessDealFactory,
    TypeContractFactory,
    TypeLicensePeriodFactory,
    TypeProductFactory,
    TypeSubscriptionFactory,
)
from api.models.Industry import Industry
from api.models.Supplier import Supplier
from api.viewsets.LicensePeriodViewSet import (
    LicensePeriodViewSet,
    column_name_mappings,
)
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource

license_period_test_resource = ViewSetTestResource(LicensePeriodViewSet, "licenses-periods-list")


@pytest.mark.django_db
class TestGetLicensePeriod:
    def test_get_license_periods_can_list_licenses_periods(
        self,
        business_deal_factory: TypeBusinessDealFactory,
        contract_factory: TypeContractFactory,
        user_with_other_buyer: User,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        """Test that we can list license periods."""
        business_deal = business_deal_factory(buyer=user_with_other_buyer.person.employer.buyer)
        contract = contract_factory(business_deal=business_deal)
        subscription = subscription_factory(contract, product)
        license_period_factory(subscription)
        license_period_factory(subscription)
        license_period_factory()

        response = license_period_test_resource.request("list", user_with_other_buyer)

        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert response.data["results"][0]["subscription"]["id"] == subscription.pk
        assert response.data["results"][0]["subscription"]["contract"]["id"] == contract.pk

        assert "calculatedTotalPrice" in response.data["results"][0]["subscription"]
        assert "calculatedTotalPricePerUser" in response.data["results"][0]["subscription"]
        assert "activeEmployeeLicenseCount" in response.data["results"][0]["subscription"]
        assert "calculatedTotalPrice" in response.data["results"][0]["subscription"]["contract"]

    def test_get_license_periods_filter_by_subscription_domain(
        self,
        user: User,
        contract: Contract,
        subscription_factory: TypeSubscriptionFactory,
        product_factory: TypeProductFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:

        # create a subscription/license period for every domain
        selected_license_period = None
        for domain, _ in DOMAINS:
            subscription = subscription_factory(product=product_factory(domain=domain), contract=contract)
            lp = license_period_factory(subscription=subscription)
            if domain == DOMAIN_INSURANCE:
                selected_license_period = lp

        response = license_period_test_resource.request("list", user, data={"domainId": DOMAIN_INSURANCE})
        print(response.data)
        assert response.status_code == status.HTTP_200_OK, response.data
        assert response.data["count"] == 1, response.data
        assert response.data["results"][0]["id"] == selected_license_period.id

    def test_get_license_periods_filter_by_product_id(
        self,
        user: User,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        product_factory: TypeProductFactory,
        contract: Contract,
        industry: Industry,
        supplier: Supplier,
    ) -> None:
        product_to_filter_to = product_factory(name="0PRODUCT", industry=industry, supplier=supplier)
        other_product = product_factory(name="1PRODUCT", industry=industry, supplier=supplier)
        expected_subscription = subscription_factory(contract, product_to_filter_to)
        subscription_to_filter = subscription_factory(contract, other_product)
        _ = license_period_factory(subscription=expected_subscription)
        _ = license_period_factory(subscription=subscription_to_filter)

        response = license_period_test_resource.request("list", user, data={"productId": product_to_filter_to.pk})
        print(response.data)
        assert response.status_code == status.HTTP_200_OK, response.data
        assert response.data["count"] == 1, response.data
        assert response.data["results"][0]["subscription"]["product"]["id"] == product_to_filter_to.pk


@pytest.mark.parametrize(
    "filter_column",
    column_name_mappings.keys(),
)
@pytest.mark.django_db
class TestListLicensePeriodFilterColumns:
    def test_column_mappings_valid(self, user: User, filter_column: str, license_period: LicensePeriod) -> None:
        response = license_period_test_resource.request(
            "list", user, data={"filterContent": f"{filter_column} equals '1'", "filterOperator": "and"}
        )
        assert response.status_code == status.HTTP_200_OK, response.data
