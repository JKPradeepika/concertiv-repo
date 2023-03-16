from copy import deepcopy
from datetime import date, timedelta
from decimal import Decimal
import json
from typing import Any, Dict, List, Optional, Tuple, Union

from moneyed import Money
import pytest
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.serializers import ErrorDetail

from api.constants import (
    LICENSE_PERIOD_TYPE_ENTERPRISE,
    LICENSE_PERIOD_TYPE_PREPAID_CREDIT,
    LICENSE_PERIOD_TYPE_USER_LIMIT,
    LICENSE_PERIOD_TYPE_PER_USER,
    LICENSE_PERIOD_TYPE_OTHER,
    CONTRACT_DURATION_UNIT_MONTHS,
    CONTRACT_DURATION_UNIT_YEARS,
    CONTRACT_STATUS_ACTIVE,
    SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY,
    SUBSCRIPTION_BILLING_FREQUENCY_MONTHLY,
    SUBSCRIPTION_BILLING_FREQUENCY_ONCE,
    DOMAINS,
    DISCOUNT_TYPE_FIXED,
    DISCOUNT_TYPE_PERCENTAGE,
)
from api.models import (
    BusinessDeal,
    Buyer,
    Contract,
    Department,
    Geography,
    Product,
    LicensePeriod,
    Subscription,
    Supplier,
    User,
    CoverageGroupRestriction,
    DepartmentRestriction,
    GeographyRestriction,
    EmployerDepartment,
    EmployerGeography,
)
from api.models.fixtures import (
    TypeBuyerFactory,
    TypeBusinessDealFactory,
    TypeContractFactory,
    TypeSupplierFactory,
    TypeEmployerGeographyFactory,
    TypeGeographyFactory,
    TypeEmployerDepartmentFactory,
    TypeCoverageGroupFactory,
    TypeEmployerCoverageGroupFactory,
    TypeSubscriptionFactory,
    TypeProductFactory,
    TypeLicensePeriodFactory,
    TypeGeographyRestrictionFactory,
    TypeDepartmentRestrictionFactory,
    TypeCoverageGroupRestrictionFactory,
    TypeSubscriptionPOSGeographyFactory,
)
from api.serializers.ContractSerializer import ContractSerializer
from api.serializers.SimpleContractSerializer import ERR_MSG_RENEWAL_CYCLE
from api.serializers.SubscriptionSerializer import SubscriptionSerializer
from api.serializers.validation_helpers import INVALID_LICENSE_PERIOD_START_DATE_ERROR_DETAIL
from api.viewsets import ContractViewSet
from api.viewsets.ContractViewSet import column_name_mappings
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource

contracts_test_resource = ViewSetTestResource(ContractViewSet, "contracts-list")

REQUIRED_FIELD_MESSAGE = "This field is required."

base_license_period_post_data = {
    "endDate": "2023-02-01",
    "price": "1000",
    "priceCurrency": "USD",
    "startDate": "2022-02-01",
}

enterprise_license_period_post_data: Dict[str, Any] = deepcopy(base_license_period_post_data)
enterprise_license_period_post_data["type"] = LICENSE_PERIOD_TYPE_ENTERPRISE
subscription_post_data: Dict[str, Any] = {
    "name": "Subscription 1",
    "notes": "Test Notes",
    "productId": None,  # Needs to be overridden
    "licensePeriods": [enterprise_license_period_post_data],
    "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY,
    "taxRate": "0.10",
    "contractId": None,  # Needs to be overridden
    "resellerSupplierId": None,
}
contract_post_data: Dict[str, Any] = {
    "autorenewalDeadline": "2023-01-01",
    "autorenewalDuration": 1,
    "autorenewalDurationUnit": CONTRACT_DURATION_UNIT_YEARS,
    "buyerEntityName": "Concertiv, Inc.",
    "buyerId": None,  # Needs to be overridden
    "signedDate": "2022-01-01",
    "status": CONTRACT_STATUS_ACTIVE,
    "supplierId": None,  # Needs to be overridden
    "terminatedAt": "2023-01-01",
    "businessDealId": None,  # Needs to be overridden
    "subscriptions": [subscription_post_data],
}

subscription_patch_data: Dict[str, Any] = {
    "name": "Subscription 2",
    "notes": "Test Notes 2",
    "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_MONTHLY,
    "taxRate": "0.10",
    "licensePeriods": [],
}
contract_patch_data: Dict[str, Any] = {
    "autorenewalDeadline": "2023-01-02",
    "autorenewalDuration": 3,
    "autorenewalDurationUnit": CONTRACT_DURATION_UNIT_MONTHS,
    "buyerEntityName": "Concertiv",
    "signedDate": "2022-01-02",
    "status": CONTRACT_STATUS_ACTIVE,
    "terminatedAt": "2023-01-01",
    "subscriptions": [subscription_post_data],
}


@pytest.mark.django_db
def post_contract(
    post_body: Dict[str, Any],
    buyer: Optional[Buyer],
    supplier: Optional[Supplier],
    user: User,
    business_deal: Optional[BusinessDeal],
) -> Response:

    data = deepcopy(post_body)
    if buyer:
        data["buyerId"] = buyer.id
    if supplier:
        data["supplierId"] = supplier.id
    if business_deal:
        data["businessDealId"] = business_deal.id

    return contracts_test_resource.request("create", user, data=json.dumps(data))


class TestContractModelPermissions:
    @pytest.mark.django_db
    def test_contract_will_prevent_get_one(self, contract: Contract, concertiv_user_with_no_permissions: User) -> None:
        response = contracts_test_resource.request("retrieve", concertiv_user_with_no_permissions, pk=contract.pk)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_contract_will_prevent_get_list(self, concertiv_user_with_no_permissions: User) -> None:
        response = contracts_test_resource.request("list", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestContractTenancy:
    @pytest.mark.django_db
    def test_contract_get_one_will_return_correct_contract(
        self,
        business_deal_factory: TypeBusinessDealFactory,
        contract_factory: TypeContractFactory,
        user_with_other_buyer: User,
    ) -> None:
        business_deal = business_deal_factory(buyer=user_with_other_buyer.person.employer.buyer)
        contract = contract_factory(business_deal=business_deal)
        response = contracts_test_resource.request("retrieve", user_with_other_buyer, pk=contract.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == contract.id

    @pytest.mark.django_db
    def test_contracts_get_one_will_not_return_bad_contract(
        self,
        business_deal_factory: TypeBusinessDealFactory,
        contract_factory: TypeContractFactory,
        user_with_other_buyer: User,
    ) -> None:
        contract = contract_factory()
        response = contracts_test_resource.request("retrieve", user_with_other_buyer, pk=contract.id)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_contracts_get_will_return_correct_contract(
        self,
        business_deal_factory: TypeBusinessDealFactory,
        contract_factory: TypeContractFactory,
        user_with_other_buyer: User,
    ) -> None:
        business_deal = business_deal_factory(buyer=user_with_other_buyer.person.employer.buyer)
        contracts_from_same_company = [
            contract_factory(business_deal=business_deal),
            contract_factory(business_deal=business_deal),
        ]
        contract_factory()

        response = contracts_test_resource.request("list", user_with_other_buyer)
        assert response.data["count"] == len(contracts_from_same_company)


class TestGetContract:
    @pytest.mark.django_db
    def test_api_can_list_contract(self, contract: Contract, user: User) -> None:
        response = contracts_test_resource.request("list", user)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == contract.pk

    @pytest.mark.django_db
    def test_api_can_list_contracts_filtered_by_buyer_id(
        self,
        business_deal_factory: TypeBusinessDealFactory,
        buyer_factory: TypeSupplierFactory,
        contract_factory: TypeContractFactory,
        user: User,
    ) -> None:
        # Create two contracts, each belonging to a different buyer
        buyer_1 = buyer_factory(short_code="ABC")
        buyer_2 = buyer_factory(short_code="DEF")
        business_deal_1 = business_deal_factory(buyer=buyer_1)
        business_deal_2 = business_deal_factory(buyer=buyer_2)
        contract_1 = contract_factory(business_deal=business_deal_1)
        contract_factory(business_deal=business_deal_2)

        response = contracts_test_resource.request("list", user, data={"buyerId": buyer_1.pk})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == contract_1.pk

    @pytest.mark.django_db
    def test_list_contracts_filter_contract_series_id(
        self,
        user: User,
        contract: Contract,
        contract_factory: TypeContractFactory,
    ) -> None:
        renewed_contract = contract_factory(previous_contract=contract)
        response = contracts_test_resource.request(
            "list", user, data={"contractSeriesId": renewed_contract.contract_series.id}
        )
        assert response.status_code == status.HTTP_200_OK, response.data
        assert response.data["count"] == 2
        assert response.data["results"][0]["id"] in [contract.id, renewed_contract.id]
        assert response.data["results"][1]["id"] in [contract.id, renewed_contract.id]

    @pytest.mark.parametrize("selected_domain", DOMAINS)
    @pytest.mark.django_db
    def test_api_can_list_contracts_filtered_by_product_domain(
        self,
        user: User,
        contract_factory: TypeContractFactory,
        subscription_factory: TypeSubscriptionFactory,
        product_factory: TypeProductFactory,
        selected_domain: Tuple[int, str],
    ) -> None:

        listed_contract = None
        for domain, _ in DOMAINS:
            c = contract_factory()
            subscription_factory(product=product_factory(domain=domain), contract=c)
            if domain == selected_domain[0]:
                listed_contract = c

        response = contracts_test_resource.request("list", user, data={"domainId": selected_domain[0]})
        assert response.status_code == status.HTTP_200_OK, response.data
        assert response.data["count"] == 1, response.data
        assert response.data["results"][0]["id"] == listed_contract.id, response.data

    @pytest.mark.django_db
    def test_api_can_fetch_contract_by_id(
        self, contract: Contract, user: User, subscription_active_factory: TypeSubscriptionFactory
    ) -> None:
        _ = subscription_active_factory(contract=contract)

        response = contracts_test_resource.request("retrieve", user, pk=contract.pk)
        assert response.status_code == status.HTTP_200_OK
        print("response data: ", response.data)

        self.assert_contract_fields(contract, response)
        first_response_subscription = self.assert_contract_subscription_fields(response)
        self.assert_contract_subscription_license_period_fields(first_response_subscription)

    @pytest.mark.django_db
    def test_subscription_active_license_period_null_when_no_active_period(
        self,
        contract: Contract,
        user: User,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract=contract)
        today = date.today()

        _ = license_period_factory(
            subscription=subscription, start_date=today - timedelta(days=2), end_date=today - timedelta(days=1)
        )

        response = contracts_test_resource.request("retrieve", user, pk=contract.pk)
        assert response.status_code == status.HTTP_200_OK, response.data
        print("response data: ", response.data)

        first_response_subscription = response.data["subscriptions"][0]
        assert first_response_subscription["activeLicensePeriod"] is None, first_response_subscription
        assert first_response_subscription["resellerSupplier"] is None, first_response_subscription

    @pytest.mark.django_db
    def test_subscription_active_license_period_gets_active_license_period(
        self,
        contract: Contract,
        user: User,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        subscription = subscription_factory(contract=contract)
        today = date.today()

        # license period already passed
        _ = license_period_factory(
            subscription=subscription, start_date=today - timedelta(days=3), end_date=today - timedelta(days=2)
        )

        assumed_active_license_period = license_period_factory(
            subscription=subscription, start_date=today - timedelta(days=1), end_date=today + timedelta(days=1)
        )

        # license period in future
        _ = license_period_factory(
            subscription=subscription, start_date=today + timedelta(days=2), end_date=today + timedelta(days=3)
        )

        response = contracts_test_resource.request("retrieve", user, pk=contract.pk)
        assert response.status_code == status.HTTP_200_OK
        print("response data: ", response.data)

        first_response_subscription = response.data["subscriptions"][0]
        assert first_response_subscription["activeLicensePeriod"]["id"] is assumed_active_license_period.pk

    def assert_contract_subscription_license_period_fields(self, first_response_subscription):
        assert "licensePeriods" in first_response_subscription
        assert len(first_response_subscription["licensePeriods"]) > 0
        first_response_license_period = first_response_subscription["licensePeriods"][0]
        database_license_period = LicensePeriod.objects.get(id=first_response_license_period["id"])
        assert first_response_license_period["type"]["id"] == database_license_period.type
        assert str(first_response_license_period["startDate"]) == str(database_license_period.start_date)
        assert str(first_response_license_period["endDate"]) == str(database_license_period.end_date)
        assert (
            Money(first_response_license_period["price"], first_response_license_period["priceCurrency"])
            == database_license_period.price
        )
        assert first_response_license_period["maxUsers"] == database_license_period.max_users
        assert first_response_license_period["maxCredits"] == database_license_period.max_credits
        assert (
            Money(
                first_response_license_period["incrementalUserPrice"],
                first_response_license_period["incrementalUserPriceCurrency"],
            )
            == database_license_period.incremental_user_price
        )

    def assert_contract_subscription_fields(self, response):
        assert "subscriptions" in response.data
        assert len(response.data["subscriptions"]) > 0
        first_response_subscription = response.data["subscriptions"][0]
        database_subscription = Subscription.objects.get(id=first_response_subscription["id"])
        assert first_response_subscription["name"] == database_subscription.name
        assert first_response_subscription["billingFrequency"]["id"] == database_subscription.billing_frequency

        assert first_response_subscription[
            "activeEmployeeLicenseCount"
        ] == SubscriptionSerializer.get_active_employee_license_count(database_subscription)
        assert "calculatedTotalPricePerUser" in first_response_subscription

        assert "taxRate" in first_response_subscription
        assert first_response_subscription["notes"] == database_subscription.notes
        assert "product" in first_response_subscription
        assert first_response_subscription["product"]["name"] == database_subscription.product.name
        assert "domain" in first_response_subscription["product"]
        assert isinstance(first_response_subscription["product"]["domain"], dict)

        assert "geographyRestrictions" in first_response_subscription
        assert "departmentRestrictions" in first_response_subscription
        assert "coverageGroupRestrictions" in first_response_subscription
        assert "activeLicensePeriod" in first_response_subscription

        return first_response_subscription

    def assert_contract_fields(self, contract, response):
        assert response.data["id"] == contract.id
        assert str(response.data["startDate"]) == str(contract.start_date)
        assert str(response.data["endDate"]) == str(contract.end_date)
        assert "supplier" in response.data
        assert response.data["supplier"]["name"] == contract.business_deal.supplier.employer.name
        assert response.data["buyerEntityName"] == contract.buyer_entity_name
        assert "calculatedTotalPrice" in response.data
        assert response.data["status"]["id"] == contract.status
        assert str(response.data["autorenewalDeadline"]) == str(contract.autorenewal_deadline)
        assert response.data["autorenewalDuration"] == contract.autorenewal_duration
        assert response.data["autorenewalDurationUnit"]["id"] == contract.autorenewal_duration_unit
        assert str(response.data["precautionaryCancellationDate"]) == str(contract.precautionary_cancellation_date)
        assert "contractSeriesId" in response.data
        assert response.data["contractSeriesId"] == getattr(contract.contract_series, "id", None)


@pytest.mark.parametrize(
    "filter_column",
    column_name_mappings.keys(),
)
@pytest.mark.django_db
class TestListContractFilterColumns:
    def test_column_mappings_valid(self, user: User, filter_column: str, contract: Contract) -> None:
        response = contracts_test_resource.request(
            "list", user, data={"filterContent": f"{filter_column} equals '1'", "filterOperator": "and"}
        )
        assert response.status_code == status.HTTP_200_OK, response.data


class TestPostContract:
    @pytest.mark.django_db
    def test_api_can_create_a_contract_with_an_enterprise_license_period(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        response = post_contract(contract_post_data, buyer, supplier, user, business_deal)
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "proposalPrice" in response.data
        assert "proposalPrice" in response.data["subscriptions"][0]
        assert "proposalPrice" in response.data["subscriptions"][0]["licensePeriods"][0]
        assert "proposalNotes" in response.data["subscriptions"][0]["licensePeriods"][0]
        assert response.data["subscriptions"][0]["licensePeriods"][0]["proposalPrice"] is None

    @pytest.mark.django_db
    def test_post_contract_with_proposal_price(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["subscriptions"][0]["licensePeriods"][0]["proposalPrice"] = "100.00"
        response = post_contract(data, buyer, supplier, user, business_deal)
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "proposalPrice" in response.data
        assert "proposalPrice" in response.data["subscriptions"][0]
        assert "proposalPrice" in response.data["subscriptions"][0]["licensePeriods"][0]
        assert "proposalNotes" in response.data["subscriptions"][0]["licensePeriods"][0]

        response_json = json.loads(response.content)
        assert response_json["subscriptions"][0]["licensePeriods"][0]["proposalPrice"] == "$100.00"
        assert response_json["subscriptions"][0]["proposalPrice"] == "$100.00"
        assert response_json["proposalPrice"] == "$100.00"
        assert response_json["subscriptions"][0]["licensePeriods"][0]["proposalNotes"] == ""

    @pytest.mark.django_db
    def test_post_contract_ignores_child_id_validation(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["subscriptions"][0]["subscriptionId"] = 0
        data["subscriptions"][0]["licensePeriods"][0]["licensePeriodId"] = 0
        response = post_contract(data, buyer, supplier, user, business_deal)
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_post_contract_not_renewal_has_null_contract_series(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        response = post_contract(data, buyer, supplier, user, business_deal)
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["contractSeriesId"] is None

    @pytest.mark.django_db
    def test_post_contract_subscription_pos_geographies(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
        geography: Geography,
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["subscriptions"][0]["posGeographyIds"] = [geography.id]
        response = post_contract(data, buyer, supplier, user, business_deal)
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data["subscriptions"][0]["posGeographies"]) == 1

    @pytest.mark.django_db
    def test_post_renewed_contract(
        self,
        user: User,
        product: Product,
        buyer: Buyer,
        supplier: Supplier,
        business_deal: BusinessDeal,
        contract_factory: TypeContractFactory,
        subscription_factory: TypeSubscriptionFactory,
    ) -> None:
        contract = contract_factory(business_deal=business_deal)
        subscription = subscription_factory(contract=contract, product=product)
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["previousContractId"] = contract.id
        response = post_contract(data, buyer, supplier, user, business_deal)
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["subscriptions"][0]["previousSubscriptionIds"] == [subscription.id]

        assert contract.contract_series is None
        contract.refresh_from_db(fields=["contract_series"])
        assert response.data["contractSeriesId"] == contract.contract_series.id

    @pytest.mark.django_db
    def test_post_renewed_contract_invalid_renewal_period(
        self,
        user: User,
        product: Product,
        buyer: Buyer,
        supplier: Supplier,
        business_deal: BusinessDeal,
        contract_factory: TypeContractFactory,
        subscription_factory: TypeSubscriptionFactory,
    ) -> None:
        contract = contract_factory(business_deal=business_deal)
        later_contract = contract_factory(business_deal=business_deal, previous_contract=contract)
        assert later_contract.contract_series
        subscription_factory(contract=contract, product=product)
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["previousContractId"] = contract.id
        response = post_contract(data, buyer, supplier, user, business_deal)
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["previousContractId"][0] == ErrorDetail(
            "Must renew a contract from the latest contract renewal period.", code="invalid"
        )

    @pytest.mark.django_db
    def test_post_renewed_contract_ignores_existing_child_ids(
        self,
        user: User,
        product: Product,
        buyer: Buyer,
        supplier: Supplier,
        business_deal: BusinessDeal,
        contract_factory: TypeContractFactory,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
    ) -> None:
        contract = contract_factory(business_deal=business_deal)
        subscription = subscription_factory(contract=contract, product=product)
        license_period = license_period_factory(subscription=subscription)
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["previousContractId"] = contract.id
        data["subscriptions"][0]["subscriptionId"] = subscription.id
        data["subscriptions"][0]["licensePeriods"][0]["licensePeriodId"] = license_period.id
        response = post_contract(data, buyer, supplier, user, business_deal)
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["subscriptions"][0]["previousSubscriptionIds"] == [subscription.id]
        assert response.data["subscriptions"][0]["id"] != subscription.id
        assert response.data["subscriptions"][0]["licensePeriods"][0] != license_period.id

    @pytest.mark.django_db
    def test_post_renewed_contract_invalid_buyer(
        self,
        user: User,
        product: Product,
        buyer: Buyer,
        supplier: Supplier,
        business_deal: BusinessDeal,
        contract_factory: TypeContractFactory,
        business_deal_factory: TypeBusinessDealFactory,
        buyer_factory: TypeBuyerFactory,
    ) -> None:
        different_buyer = buyer_factory(name="Not Concertiv", short_code="NC")
        different_business_deal = business_deal_factory(buyer=different_buyer)
        contract = contract_factory(business_deal=different_business_deal)
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["previousContractId"] = contract.id
        response = post_contract(data, buyer, supplier, user, business_deal)
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["previousContractId"][0].code == "does_not_exist", response.data

    @pytest.mark.django_db
    def test_post_contracts_creates_a_contract(
        self, buyer: Buyer, product: Product, supplier: Supplier, user: User, business_deal: BusinessDeal
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        response = post_contract(contract_post_data, buyer, supplier, user, business_deal)
        contract: Union[Contract, None] = Contract.objects.first()

        print(f"Response Data: {response.data}")
        print(f"Contract: {contract}")
        assert response.status_code == status.HTTP_201_CREATED
        assert Contract.objects.count() == 1
        assert contract is not None
        assert contract.business_deal is not None
        assert contract.status == contract_post_data["status"]
        assert contract.signed_date == date.fromisoformat(contract_post_data["signedDate"])
        assert contract.autorenewal_duration == contract_post_data["autorenewalDuration"]
        assert contract.autorenewal_duration_unit == contract_post_data["autorenewalDurationUnit"]
        assert contract.autorenewal_deadline == date.fromisoformat(contract_post_data["autorenewalDeadline"])
        assert contract.terminated_at == date.fromisoformat(contract_post_data["terminatedAt"])

    @pytest.mark.django_db
    def test_post_contracts_creates_a_business_deal(
        self, buyer: Buyer, product: Product, supplier: Supplier, user: User, business_deal: BusinessDeal
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        assert BusinessDeal.objects.count() == 1
        response = post_contract(contract_post_data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}")
        print(f"Business Deal: {business_deal}")
        assert response.status_code == status.HTTP_201_CREATED
        assert BusinessDeal.objects.count() == 1
        assert business_deal is not None
        assert business_deal.buyer == buyer
        assert business_deal.supplier == supplier

    @pytest.mark.django_db
    def test_post_contract_with_office_restriction(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
        employer_geography_factory: TypeEmployerGeographyFactory,
        geography_factory: TypeGeographyFactory,
    ) -> None:
        geography = geography_factory()
        employer_geography = employer_geography_factory(geography=geography, employer=buyer.employer)
        local_contract_post_data = deepcopy(contract_post_data)

        restrictions: Dict[str, Any] = {
            "employerGeographyIds": [employer_geography.pk],
        }

        my_subscription: Dict[str, Any] = {
            "name": "Subscription 1",
            "notes": "Test Notes",
            "productId": product.pk,
            "licensePeriods": [enterprise_license_period_post_data],
            "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY,
            "taxRate": "0.10",
            "contractId": None,
            "restrictions": restrictions,
        }

        local_contract_post_data["subscriptions"][0] = my_subscription

        response = post_contract(local_contract_post_data, buyer, supplier, user, business_deal)
        print("response data: ", response.data)
        subscription: Union[Subscription, None] = Subscription.objects.latest("pk")
        assert subscription.product.pk == product.pk

        response = contracts_test_resource.request("retrieve", user, pk=response.data["id"])
        print("subscription data: ", response.data["subscriptions"][0])
        response_restrictions = response.data["subscriptions"][0]["geographyRestrictions"]
        assert len(response_restrictions) == 1
        assert response_restrictions[0]["employerGeographyId"] == employer_geography.pk
        assert response_restrictions[0]["name"] == employer_geography.name

    @pytest.mark.django_db
    def test_post_contract_with_department_restriction(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
        employer_department_factory: TypeEmployerDepartmentFactory,
        department: Department,
    ) -> None:
        employer_department = employer_department_factory(department=department, employer=buyer.employer)
        local_contract_post_data = deepcopy(contract_post_data)

        restrictions: Dict[str, Any] = {
            "employerDepartmentIds": [employer_department.pk],
        }

        my_subscription: Dict[str, Any] = {
            "name": "Subscription 1",
            "notes": "Test Notes",
            "productId": product.pk,
            "licensePeriods": [enterprise_license_period_post_data],
            "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY,
            "taxRate": "0.10",
            "contractId": None,  # Needs to be overridden
            "restrictions": restrictions,
        }

        local_contract_post_data["subscriptions"][0] = my_subscription

        response = post_contract(local_contract_post_data, buyer, supplier, user, business_deal)
        print("response data: ", response.data)
        subscription: Union[Subscription, None] = Subscription.objects.latest("pk")
        assert subscription.product.pk == product.pk

        response = contracts_test_resource.request("retrieve", user, pk=response.data["id"])
        print("subscription data: ", response.data["subscriptions"][0])
        response_restrictions = response.data["subscriptions"][0]["departmentRestrictions"]
        assert len(response_restrictions) == 1
        assert response_restrictions[0]["employerDepartmentId"] == employer_department.pk
        assert response_restrictions[0]["name"] == employer_department.name

    @pytest.mark.django_db
    def test_post_contract_with_coverage_group_restriction(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
        employer_coverage_group_factory: TypeEmployerCoverageGroupFactory,
        coverage_group_factory: TypeCoverageGroupFactory,
    ) -> None:
        coverage_group = coverage_group_factory()
        employer_coverage_group = employer_coverage_group_factory(
            coverage_group=coverage_group, employer=buyer.employer
        )
        local_contract_post_data = deepcopy(contract_post_data)

        restrictions: Dict[str, Any] = {
            "employerCoverageGroupIds": [employer_coverage_group.pk],
        }

        my_subscription: Dict[str, Any] = {
            "name": "Subscription 1",
            "notes": "Test Notes",
            "productId": product.pk,
            "licensePeriods": [enterprise_license_period_post_data],
            "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY,
            "taxRate": "0.10",
            "contractId": None,  # Needs to be overridden
            "restrictions": restrictions,
        }

        local_contract_post_data["subscriptions"][0] = my_subscription

        response = post_contract(local_contract_post_data, buyer, supplier, user, business_deal)
        print("response data: ", response.data)
        subscription: Union[Subscription, None] = Subscription.objects.latest("pk")
        assert subscription.product.pk == product.pk

        response = contracts_test_resource.request("retrieve", user, pk=response.data["id"])
        print("subscription data: ", response.data["subscriptions"][0])
        response_restrictions = response.data["subscriptions"][0]["coverageGroupRestrictions"]
        assert len(response_restrictions) == 1
        assert response_restrictions[0]["employerCoverageGroupId"] == employer_coverage_group.pk
        assert response_restrictions[0]["name"] == employer_coverage_group.name

    @pytest.mark.django_db
    def test_post_contract_with_office_department_and_coverage_group_restrictions(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
        employer_geography_factory: TypeEmployerGeographyFactory,
        geography_factory: TypeGeographyFactory,
        employer_department_factory: TypeEmployerDepartmentFactory,
        department: Department,
        employer_coverage_group_factory: TypeEmployerCoverageGroupFactory,
        coverage_group_factory: TypeCoverageGroupFactory,
    ) -> None:
        geography = geography_factory()
        employer_geography = employer_geography_factory(geography=geography, employer=buyer.employer)

        employer_department = employer_department_factory(department=department, employer=buyer.employer)

        coverage_group = coverage_group_factory()
        employer_coverage_group = employer_coverage_group_factory(
            coverage_group=coverage_group, employer=buyer.employer
        )

        local_contract_post_data = deepcopy(contract_post_data)

        restrictions: Dict[str, Any] = {
            "employerGeographyIds": [employer_geography.pk],
            "employerDepartmentIds": [employer_department.pk],
            "employerCoverageGroupIds": [employer_coverage_group.pk],
        }

        my_subscription: Dict[str, Any] = {
            "name": "Subscription 1",
            "notes": "Test Notes",
            "productId": product.pk,
            "licensePeriods": [enterprise_license_period_post_data],
            "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY,
            "taxRate": "0.10",
            "contractId": None,
            "restrictions": restrictions,
        }

        local_contract_post_data["subscriptions"][0] = my_subscription

        response = post_contract(local_contract_post_data, buyer, supplier, user, business_deal)
        print("response data: ", response.data)
        subscription: Union[Subscription, None] = Subscription.objects.latest("pk")
        assert subscription.product.pk == product.pk

        response = contracts_test_resource.request("retrieve", user, pk=response.data["id"])
        print("subscription data: ", response.data["subscriptions"][0])

        response_geography_restrictions = response.data["subscriptions"][0]["geographyRestrictions"]
        assert len(response_geography_restrictions) == 1
        assert response_geography_restrictions[0]["employerGeographyId"] == employer_geography.pk

        response_department_restrictions = response.data["subscriptions"][0]["departmentRestrictions"]
        assert len(response_department_restrictions) == 1
        assert response_department_restrictions[0]["employerDepartmentId"] == employer_department.pk

        response_coverage_group_restrictions = response.data["subscriptions"][0]["coverageGroupRestrictions"]
        assert len(response_coverage_group_restrictions) == 1
        assert response_coverage_group_restrictions[0]["employerCoverageGroupId"] == employer_coverage_group.pk

    @pytest.mark.django_db
    def test_post_contract_with_multiple_office_restrictions(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
        employer_geography_factory: TypeEmployerGeographyFactory,
        geography_factory: TypeGeographyFactory,
    ) -> None:
        geography = geography_factory()
        first_employer_geography = employer_geography_factory(
            geography=geography, employer=buyer.employer, name="first"
        )
        second_employer_geography = employer_geography_factory(
            geography=geography, employer=buyer.employer, name="second"
        )
        third_employer_geography = employer_geography_factory(
            geography=geography, employer=buyer.employer, name="third"
        )
        local_contract_post_data = deepcopy(contract_post_data)

        restrictions: Dict[str, Any] = {
            "employerGeographyIds": [
                first_employer_geography.pk,
                second_employer_geography.pk,
                third_employer_geography.pk,
            ],
        }

        my_subscription: Dict[str, Any] = {
            "name": "Subscription 1",
            "notes": "Test Notes",
            "productId": product.pk,
            "licensePeriods": [enterprise_license_period_post_data],
            "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY,
            "taxRate": "0.10",
            "contractId": None,
            "restrictions": restrictions,
        }

        local_contract_post_data["subscriptions"][0] = my_subscription

        response = post_contract(local_contract_post_data, buyer, supplier, user, business_deal)
        print("response data: ", response.data)
        subscription: Union[Subscription, None] = Subscription.objects.latest("pk")
        assert subscription.product.pk == product.pk

        response = contracts_test_resource.request("retrieve", user, pk=response.data["id"])
        print("subscription data: ", response.data["subscriptions"][0])
        response_restrictions = response.data["subscriptions"][0]["geographyRestrictions"]
        assert len(response_restrictions) == 3

    @pytest.mark.django_db
    def test_create_office_restriction_after_subscription_creation(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
        geography_restriction_factory: TypeGeographyRestrictionFactory,
        employer_geography_factory: TypeEmployerGeographyFactory,
        geography_factory: TypeGeographyFactory,
    ) -> None:
        geography = geography_factory()
        employer_geography = employer_geography_factory(geography=geography, employer=buyer.employer)
        local_contract_post_data = deepcopy(contract_post_data)

        restrictions: Dict[str, Any] = {
            "employerGeographyIds": [employer_geography.pk],
        }

        my_subscription: Dict[str, Any] = {
            "name": "Subscription 1",
            "notes": "Test Notes",
            "productId": product.pk,
            "licensePeriods": [enterprise_license_period_post_data],
            "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY,
            "taxRate": "0.10",
            "contractId": None,  # Needs to be overridden
            "restrictions": restrictions,
        }

        local_contract_post_data["subscriptions"][0] = my_subscription

        response = post_contract(local_contract_post_data, buyer, supplier, user, business_deal)
        subscription: Union[Subscription, None] = Subscription.objects.latest("pk")
        geography_restriction_factory(
            subscription=subscription, employer_geography=employer_geography_factory(geography=geography_factory())
        )

        response = contracts_test_resource.request("retrieve", user, pk=response.data["id"])
        response_geography_restrictions = response.data["subscriptions"][0]["geographyRestrictions"]
        assert len(response_geography_restrictions) == 2

    @pytest.mark.django_db
    def test_post_contracts_creates_a_subscription(
        self, buyer: Buyer, product: Product, supplier: Supplier, user: User, business_deal: BusinessDeal
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        response = post_contract(contract_post_data, buyer, supplier, user, business_deal)
        subscription: Union[Subscription, None] = Subscription.objects.first()

        print(f"Response Data: {response.data}")
        print(f"Subscription: {subscription}")
        assert response.status_code == status.HTTP_201_CREATED
        assert Subscription.objects.count() == 1
        assert subscription is not None
        assert subscription.contract.business_deal == business_deal
        assert subscription.product == product
        assert subscription.name == contract_post_data["subscriptions"][0]["name"]

    @pytest.mark.django_db
    def test_post_contracts_invalid_second_license_period_start_date(
        self, buyer: Buyer, product: Product, supplier: Supplier, user: User, business_deal: BusinessDeal
    ) -> None:
        """Request should fail due to second license period having same start date as first."""
        alt_subscription_1_license_period_1 = deepcopy(base_license_period_post_data)
        alt_subscription_1_license_period_1["type"] = LICENSE_PERIOD_TYPE_USER_LIMIT
        alt_subscription_1_license_period_1["maxUsers"] = 10

        alt_subscription_1_license_period_2 = deepcopy(base_license_period_post_data)
        alt_subscription_1_license_period_2["type"] = LICENSE_PERIOD_TYPE_PREPAID_CREDIT
        alt_subscription_1_license_period_2["maxCredits"] = 100

        alt_subscription_1_post_data: Dict[str, Any] = {
            "name": "Subscription 2",
            "notes": "Test Notes 2",
            "productId": product.pk,
            "licensePeriods": [alt_subscription_1_license_period_1, alt_subscription_1_license_period_2],
            "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_MONTHLY,
            "taxRate": "0.20",
            "contractId": None,
        }
        alt_subscription_2_post_data: Dict[str, Any] = {
            "name": "Subscription 3",
            "notes": "Test Notes 3",
            "productId": product.pk,
            "licensePeriods": [],
            "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_ONCE,
            "taxRate": "0.20",
            "contractId": None,
        }

        alt_contract_post_data: Dict[str, Any] = {
            "autorenewalDeadline": "2023-02-02",
            "autorenewalDuration": 2,
            "autorenewalDurationUnit": CONTRACT_DURATION_UNIT_MONTHS,
            "buyerEntityName": "Test Buyer Entity Name",
            "buyerId": None,
            "signedDate": "2022-02-02",
            "status": CONTRACT_STATUS_ACTIVE,
            "supplierId": None,
            "terminatedAt": "2023-02-02",
            "businessDealId": None,
            "subscriptions": [alt_subscription_1_post_data, alt_subscription_2_post_data],
        }

        response = post_contract(alt_contract_post_data, buyer, supplier, user, business_deal)
        print(f"Response Data: {response.data}")
        assert len(response.data["subscriptions"]) >= 2
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["subscriptions"][0]["licensePeriods"][1]["startDate"] == [
            INVALID_LICENSE_PERIOD_START_DATE_ERROR_DETAIL
        ]

    @pytest.mark.django_db
    def test_post_contracts_creates_a_license_period(
        self, buyer: Buyer, product: Product, supplier: Supplier, user: User, business_deal: BusinessDeal
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        response = post_contract(contract_post_data, buyer, supplier, user, business_deal)
        license_period = LicensePeriod.objects.first()
        subscription: Union[Subscription, None] = Subscription.objects.first()

        print(f"Response Data: {response.data}")
        print(f"License Period: {license_period}")
        assert response.status_code == status.HTTP_201_CREATED
        assert LicensePeriod.objects.count() == 1
        assert license_period is not None
        assert license_period.subscription == subscription
        assert license_period.subscription.billing_frequency == subscription_post_data["billingFrequency"]
        assert license_period.end_date == date.fromisoformat(base_license_period_post_data["endDate"])
        assert license_period.price == Money(
            base_license_period_post_data["price"], base_license_period_post_data["priceCurrency"]
        )
        assert license_period.start_date == date.fromisoformat(base_license_period_post_data["startDate"])
        assert license_period.subscription.tax_rate == Decimal(subscription_post_data["taxRate"])
        assert license_period.type == contract_post_data["subscriptions"][0]["licensePeriods"][0]["type"]

    @pytest.mark.django_db
    def test_post_contracts_uses_an_existing_business_deal_when_provided(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        data = deepcopy(contract_post_data)
        data["businessDealId"] = business_deal.id
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["businessDealId"] == business_deal.id
        assert BusinessDeal.objects.count() == 1

    @pytest.mark.django_db
    def test_post_contracts_sets_the_exchange_rate_to_usd_automatically(
        self, buyer: Buyer, product: Product, supplier: Supplier, user: User, business_deal: BusinessDeal
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        response = post_contract(contract_post_data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["subscriptions"][0]["licensePeriods"][0]["exchangeRateToUsdAtTimeOfPurchase"] is not None

    @pytest.mark.django_db
    def test_post_contracts_can_create_multiple_subscriptions(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
        employer_department: EmployerDepartment,
        employer_geography: EmployerGeography,
    ) -> None:
        alt_subscription_1_license_period_1 = deepcopy(base_license_period_post_data)
        alt_subscription_1_license_period_1["type"] = LICENSE_PERIOD_TYPE_USER_LIMIT
        alt_subscription_1_license_period_1["maxUsers"] = 10

        alt_subscription_1_license_period_2 = deepcopy(base_license_period_post_data)
        alt_subscription_1_license_period_2["type"] = LICENSE_PERIOD_TYPE_PREPAID_CREDIT
        alt_subscription_1_license_period_2["maxCredits"] = 100
        del alt_subscription_1_license_period_2["startDate"]
        alt_subscription_1_license_period_2["endDate"] = "2024-02-01"

        alt_subscription_1_post_data: Dict[str, Any] = {
            "name": "Subscription 2",
            "notes": "Test Notes 2",
            "productId": product.pk,
            "licensePeriods": [alt_subscription_1_license_period_1, alt_subscription_1_license_period_2],
            "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_MONTHLY,
            "taxRate": "0.20",
            "contractId": None,
            "restrictions": {"employerGeographyIds": [employer_geography.id]},
        }
        alt_subscription_2_post_data: Dict[str, Any] = {
            "name": "Subscription 3",
            "notes": "Test Notes 3",
            "productId": product.pk,
            "licensePeriods": [],
            "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_ONCE,
            "taxRate": "0.20",
            "contractId": None,
            "restrictions": {"employerDepartmentIds": [employer_department.id]},
        }

        alt_contract_post_data: Dict[str, Any] = {
            "autorenewalDeadline": "2023-02-02",
            "autorenewalDuration": 2,
            "autorenewalDurationUnit": CONTRACT_DURATION_UNIT_MONTHS,
            "buyerEntityName": "Test Buyer Entity Name",
            "buyerId": None,
            "signedDate": "2022-02-02",
            "status": CONTRACT_STATUS_ACTIVE,
            "supplierId": None,
            "terminatedAt": "2023-02-02",
            "businessDealId": None,
            "subscriptions": [alt_subscription_1_post_data, alt_subscription_2_post_data],
        }

        response = post_contract(alt_contract_post_data, buyer, supplier, user, business_deal)
        print(f"Response Data: {response.data}")
        print("")
        print(
            [
                {
                    "geo": x["geographyRestrictions"],
                    "dept": x["departmentRestrictions"],
                    "cov": x["coverageGroupRestrictions"],
                }
                for x in response.data["subscriptions"]
            ]
        )
        assert len(response.data["subscriptions"]) >= 2
        assert response.status_code == status.HTTP_201_CREATED
        subscription_1 = Subscription.objects.get(id=response.data["subscriptionIds"][0])
        subscription_2 = Subscription.objects.get(id=response.data["subscriptionIds"][1])
        assert subscription_1 is not None
        assert subscription_2 is not None
        assert subscription_1.contract.business_deal == business_deal
        assert subscription_1.product == product
        subscription_names = [x["name"] for x in response.data["subscriptions"]]
        assert alt_contract_post_data["subscriptions"][0]["name"] in subscription_names
        assert alt_contract_post_data["subscriptions"][1]["name"] in subscription_names

        assert subscription_1.geography_restrictions.exists() or subscription_1.department_restrictions.exists()
        assert subscription_2.geography_restrictions.exists() or subscription_2.department_restrictions.exists()

        subscription_1_licenses_periods = response.data["subscriptions"][0]["licensePeriods"]
        subscription_2_licenses_periods = response.data["subscriptions"][1]["licensePeriods"]
        added_license_period_types = [
            x["type"]["id"] for x in subscription_1_licenses_periods + subscription_2_licenses_periods
        ]
        assert alt_subscription_1_license_period_1["type"] in added_license_period_types
        assert alt_subscription_1_license_period_2["type"] in added_license_period_types

        assert (
            "calculatedTotalPrice" in subscription_1_licenses_periods[0]
            if subscription_1_licenses_periods
            else subscription_2_licenses_periods[0]
        )
        assert "calculatedTotalPrice" in response.data["subscriptions"][0]
        assert "calculatedTotalPrice" in response.data

        assert "calculatedTotalPricePerUser" in response.data["subscriptions"][0]
        assert "activeEmployeeLicenseCount" in response.data["subscriptions"][0]


class TestRequiredAndOptionalFieldValidations:
    @pytest.mark.django_db
    def test_setting_precautionary_cancellation_date_with_autorenew_passes(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["precautionaryCancellationDate"] = "2023-12-31"
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["precautionaryCancellationDate"] == data["precautionaryCancellationDate"]

    @pytest.mark.django_db
    def test_setting_precautionary_cancellation_date_without_autorenew_fails(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        for field_name in ContractSerializer.get_autorenew_field_names():
            if field_name in data:
                del data[field_name]
        data["precautionaryCancellationDate"] = "2023-12-31"
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        for field_name in ContractSerializer.get_autorenew_field_names():
            if field_name == "precautionaryCancellationDate":
                continue
            assert field_name in response.data
            assert response.data.get(field_name)[0] == exceptions.ErrorDetail(REQUIRED_FIELD_MESSAGE, code="required")

    @pytest.mark.django_db
    def test_setting_reseller_supplier_id_passes(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
        supplier_factory: TypeSupplierFactory,
    ) -> None:
        reseller_supplier = supplier_factory()
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["subscriptions"][0]["resellerSupplierId"] = reseller_supplier.id
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert response.data["subscriptions"][0]["resellerSupplier"]["id"] == reseller_supplier.id, response.data[
            "subscriptions"
        ][0]

    @pytest.mark.django_db
    def test_setting_tmc_supplier_id_passes(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
        supplier_factory: TypeSupplierFactory,
    ) -> None:
        tmc_supplier = supplier_factory()
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["subscriptions"][0]["tmcSupplierId"] = tmc_supplier.id
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert response.data["subscriptions"][0]["tmcSupplier"]["id"] == tmc_supplier.id, response.data[
            "subscriptions"
        ][0]

    @pytest.mark.django_db
    def test_setting_reseller_supplier_null_passes(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["subscriptions"][0]["resellerSupplierId"] = None
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert response.data["subscriptions"][0]["resellerSupplier"] is None

    @pytest.mark.django_db
    def test_setting_tmc_supplier_null_passes(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["subscriptions"][0]["tmcSupplierId"] = None
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert response.data["subscriptions"][0]["tmcSupplier"] is None

    @pytest.mark.django_db
    def test_setting_reseller_supplier_invalid_id_fails(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["subscriptions"][0]["resellerSupplierId"] = 69
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data
        assert response.data["subscriptions"][0]["resellerSupplierId"][0] == ErrorDetail(
            string='Invalid pk "69" - object does not exist.',
            code="does_not_exist",
        )

    @pytest.mark.django_db
    def test_setting_tmc_supplier_invalid_id_fails(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["subscriptions"][0]["tmcSupplierId"] = 69
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data
        assert response.data["subscriptions"][0]["tmcSupplierId"][0] == ErrorDetail(
            string='Invalid pk "69" - object does not exist.',
            code="does_not_exist",
        )

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "discount_type",
        [DISCOUNT_TYPE_FIXED, DISCOUNT_TYPE_PERCENTAGE, None],
    )
    def test_discount_type_is_settable(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
        discount_type: Optional[int],
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["subscriptions"][0]["discountType"] = discount_type
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_201_CREATED, response.data
        if discount_type:
            assert response.data["subscriptions"][0]["discountType"].get("id") == discount_type
        else:
            assert response.data["subscriptions"][0]["discountType"] == discount_type

    @pytest.mark.django_db
    def test_discount_type_must_be_valid_choice(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        data["subscriptions"][0]["discountType"] = 69
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data
        assert response.data["subscriptions"][0]["discountType"][0] == ErrorDetail(
            string='"69" is not a valid choice.',
            code="invalid_choice",
        ), response.data

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "field_name",
        [x for x in ContractSerializer.get_autorenew_field_names() if x != "precautionaryCancellationDate"],
    )
    def test_partial_setting_autorenew_fields_fails(
        self,
        field_name: str,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        if field_name in data:
            del data[field_name]
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert field_name in response.data
        assert response.data.get(field_name)[0] == exceptions.ErrorDetail(REQUIRED_FIELD_MESSAGE, code="required")

    @pytest.mark.django_db
    def test_setting_no_autorenew_fields_passes(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["productId"] = product.pk
        for field_name in ContractSerializer.get_autorenew_field_names():
            if field_name in data:
                del data[field_name]
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "field_name",
        ["buyerEntityName", "status"],
    )
    def test_post_contracts_validates_required_contract_fields(
        self,
        field_name: str,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        data = deepcopy(contract_post_data)
        del data[field_name]
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get(field_name)[0] == exceptions.ErrorDetail(REQUIRED_FIELD_MESSAGE, code="required")

    @pytest.mark.django_db
    def test_post_contracts_validates_that_the_buyer_and_supplier_are_provided(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        # Treat buyer & supplier differently because we need to modify the call to `post_contract`
        data_without_buyer = deepcopy(contract_post_data)
        del data_without_buyer["buyerId"]
        response_without_buyer = post_contract(data_without_buyer, None, supplier, user, business_deal)

        data_without_supplier = deepcopy(contract_post_data)
        del data_without_supplier["supplierId"]
        response_without_supplier = post_contract(data_without_supplier, buyer, None, user, business_deal)

        assert response_without_buyer.status_code == status.HTTP_400_BAD_REQUEST
        assert response_without_buyer.data.get("buyerId")[0] == exceptions.ErrorDetail(
            REQUIRED_FIELD_MESSAGE, code="required"
        )
        assert response_without_supplier.status_code == status.HTTP_400_BAD_REQUEST
        assert response_without_supplier.data.get("supplierId")[0] == exceptions.ErrorDetail(
            REQUIRED_FIELD_MESSAGE, code="required"
        )

    @pytest.mark.django_db
    def test_api_can_create_a_contract_with_blank_notes_field(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        data = deepcopy(contract_post_data)
        data["subscriptions"][0]["notes"] = ""
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "field_name",
        [
            "businessDealId",
            "terminatedAt",
            "discountType",
            "resellerSupplierId",
            "tmcSupplierId",
            "posGeographyIds",
            "signedDate",
        ],
    )
    def test_post_contracts_allows_optional_contract_fields_to_be_omitted(
        self,
        field_name: str,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        data = deepcopy(contract_post_data)
        if field_name in data:
            del data[field_name]
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "field_name",
        [
            "name",
            "licensePeriods",
        ],
    )
    def test_post_contracts_validates_required_subscription_fields(
        self,
        field_name: str,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        data = deepcopy(contract_post_data)
        del data["subscriptions"][0][field_name]
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["subscriptions"][0][field_name][0] == exceptions.ErrorDetail(
            REQUIRED_FIELD_MESSAGE, code="required"
        )

    @pytest.mark.django_db
    def test_post_contracts_validates_that_the_product_is_provided(
        self, buyer: Buyer, product: Product, supplier: Supplier, user: User, business_deal: BusinessDeal
    ) -> None:
        data = deepcopy(contract_post_data)
        del data["subscriptions"][0]["productId"]
        response = post_contract(data, buyer, supplier, user, business_deal)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["subscriptions"][0]["productId"][0] == exceptions.ErrorDetail(
            REQUIRED_FIELD_MESSAGE, code="required"
        )

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "field_name",
        [
            "businessDealId",
            "notes",
        ],
    )
    def test_post_contracts_allows_optional_subscription_fields_to_be_omitted(
        self,
        field_name: str,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        data = deepcopy(contract_post_data)
        if field_name in data["subscriptions"][0]:
            del data["subscriptions"][0][field_name]
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "field_name",
        [
            "endDate",
            "price",
            "priceCurrency",
            "startDate",
            "type",
        ],
    )
    def test_post_contracts_validates_required_license_period_fields(
        self,
        field_name: str,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        data = deepcopy(contract_post_data)
        del data["subscriptions"][0]["licensePeriods"][0][field_name]
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["subscriptions"][0]["licensePeriods"][0][field_name][0] == exceptions.ErrorDetail(
            REQUIRED_FIELD_MESSAGE, code="required"
        )

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "field_name",
        [
            "incrementalUserPrice",
            "incrementalUserPriceCurrency",
            "maxCredits",
            "maxUsers",
            "usageUnit",
            "usageUnitPrice",
            "usageUnitPriceCurrency",
        ],
    )
    def test_post_contracts_allows_optional_spend_obligation_fields_to_be_omitted(
        self,
        field_name: str,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        data = deepcopy(contract_post_data)
        if field_name in data["subscriptions"][0]["licensePeriods"][0]:
            del data["subscriptions"][0]["licensePeriods"][0][field_name]
        response = post_contract(data, buyer, supplier, user, business_deal)

        print(f"Response Data: {response.data}\n")
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_post_contracts_multiple_license_periods_missing_required_fields(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        license_periods = []
        license_types_to_missing_keys = {
            LICENSE_PERIOD_TYPE_ENTERPRISE: [],
            LICENSE_PERIOD_TYPE_USER_LIMIT: ["maxUsers"],
            LICENSE_PERIOD_TYPE_PER_USER: [],
            LICENSE_PERIOD_TYPE_PREPAID_CREDIT: ["maxCredits"],
            LICENSE_PERIOD_TYPE_OTHER: [],
        }
        for license_type in license_types_to_missing_keys:
            license_period_data = deepcopy(base_license_period_post_data)
            license_period_data["type"] = license_type
            license_periods.append(license_period_data)

        alt_contract_post_data: Dict[str, Any] = {
            "autorenewalDeadline": "2023-02-02",
            "autorenewalDuration": 2,
            "autorenewalDurationUnit": CONTRACT_DURATION_UNIT_MONTHS,
            "buyerEntityName": "Test Buyer Entity Name",
            "buyerId": None,
            "signedDate": "2022-02-02",
            "status": CONTRACT_STATUS_ACTIVE,
            "supplierId": None,
            "terminatedAt": "2023-02-02",
            "businessDealId": None,
            "subscriptions": [
                {
                    "name": "Subscription hello",
                    "notes": "Test Notes 2",
                    "productId": product.pk,
                    "licensePeriods": license_periods,
                    "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_MONTHLY,
                    "taxRate": "0.20",
                    "contractId": None,
                }
            ],
        }
        response = post_contract(alt_contract_post_data, buyer, supplier, user, business_deal)
        print(f"Response Data: {response.data}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert len(response.data["subscriptions"]) == 1
        response_license_periods: List[Dict] = response.data["subscriptions"][0]["licensePeriods"]
        assert len(response_license_periods) == len(license_types_to_missing_keys)

        for i, license_period in enumerate(response_license_periods):
            expected_missing_keys = license_types_to_missing_keys[list(license_types_to_missing_keys.keys())[i]]
            assert expected_missing_keys == list(license_period.keys())
            for missing_key in expected_missing_keys:
                assert license_period[missing_key] == [exceptions.ErrorDetail(REQUIRED_FIELD_MESSAGE, "required")]

    @pytest.mark.django_db
    def test_post_contracts_multiple_license_periods_ignore_invisible_fields(
        self,
        buyer: Buyer,
        product: Product,
        supplier: Supplier,
        user: User,
        business_deal: BusinessDeal,
    ) -> None:
        license_periods = []
        license_types_ignored_and_missing_keys: Dict[int, Dict[str, Dict[str, Any]]] = {
            LICENSE_PERIOD_TYPE_ENTERPRISE: {
                "add_required": {},
                "ignored": {
                    "maxUsers": 10,
                    "maxCredits": 101,
                    "incrementalUserPrice": 1.23,
                    "incrementalUserPriceCurrency": "CAD",
                },
            },
            LICENSE_PERIOD_TYPE_USER_LIMIT: {
                "add_required": {"maxUsers": 10},
                "ignored": {"maxCredits": 102},
            },
            LICENSE_PERIOD_TYPE_PER_USER: {
                "add_required": {},
                "ignored": {"maxCredits": 103},
            },
            LICENSE_PERIOD_TYPE_PREPAID_CREDIT: {
                "add_required": {"maxCredits": 104},
                "ignored": {"maxUsers": 10},
            },
            LICENSE_PERIOD_TYPE_OTHER: {
                "add_required": {},
                "ignored": {
                    "maxUsers": 10,
                    "maxCredits": 105,
                    "incrementalUserPrice": 1.23,
                    "incrementalUserPriceCurrency": "CAD",
                },
            },
        }
        for license_type, key_categories_dicts in license_types_ignored_and_missing_keys.items():
            license_period_data = deepcopy(base_license_period_post_data)
            license_period_data["type"] = license_type
            license_period_data.update(key_categories_dicts["add_required"])
            license_period_data.update(key_categories_dicts["ignored"])
            if license_periods:
                del license_period_data["startDate"]
                license_period_data["endDate"] = (
                    date.fromisoformat(license_periods[-1]["endDate"]) + timedelta(days=2)
                ).isoformat()
            license_periods.append(license_period_data)

        alt_contract_post_data: Dict[str, Any] = {
            "autorenewalDeadline": "2023-02-02",
            "autorenewalDuration": 2,
            "autorenewalDurationUnit": CONTRACT_DURATION_UNIT_MONTHS,
            "buyerEntityName": "Test Buyer Entity Name 2",
            "buyerId": None,
            "signedDate": "2022-02-02",
            "status": CONTRACT_STATUS_ACTIVE,
            "supplierId": None,
            "terminatedAt": "2023-02-02",
            "businessDealId": None,
            "subscriptions": [
                {
                    "name": "Subscription whee",
                    "notes": "Test Notes 2",
                    "productId": product.pk,
                    "licensePeriods": license_periods,
                    "billingFrequency": SUBSCRIPTION_BILLING_FREQUENCY_MONTHLY,
                    "taxRate": "0.20",
                    "contractId": None,
                }
            ],
        }
        response = post_contract(alt_contract_post_data, buyer, supplier, user, business_deal)
        print(f"Response Data: {response.data}")
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data["subscriptions"]) == 1

        response_license_periods: List[Dict] = response.data["subscriptions"][0]["licensePeriods"]
        assert len(response_license_periods) == len(license_types_ignored_and_missing_keys)

        for license_period in response_license_periods:
            expected_ignored_keys = license_types_ignored_and_missing_keys[license_period["type"]["id"]]["ignored"]
            for missing_key in expected_ignored_keys:
                assert license_period[missing_key] != expected_ignored_keys[missing_key]


class TestCustomValidations:
    @pytest.mark.django_db
    def test_post_contracts_responds_with_an_error_when_the_business_deal_does_not_exist(
        self, buyer: Buyer, product: Product, supplier: Supplier, user: User
    ) -> None:
        contract_post_data["subscriptions"][0]["productId"] = product.pk
        data = deepcopy(contract_post_data)
        data["businessDealId"] = 69
        response = post_contract(data, buyer, supplier, user, None)

        print(f"Response Data: {response.data}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("businessDealId") == exceptions.ErrorDetail(
            string='Invalid pk "69" - object does not exist.', code="does_not_exist"
        )


@pytest.mark.django_db
class TestUpdateContract:
    def test_patch_contract(
        self,
        user: User,
        contract: Contract,
        product: Product,
        subscription_factory: TypeSubscriptionFactory,
        license_period_factory: TypeLicensePeriodFactory,
        coverage_group_restriction_factory: TypeCoverageGroupRestrictionFactory,
        department_restriction_factory: TypeDepartmentRestrictionFactory,
        geography_restriction_factory: TypeGeographyRestrictionFactory,
    ) -> None:
        """
        This test demonstrates all new fields added to support patching a contract.
        When patching a contract, in addition to changing fields on the contract record, you can:

        - create new subscriptions (included in contract patch data)
        - delete existing subscriptions
        - update existing subscriptions
        - create new license periods on new and existing subscriptions (must follow contiguous date restrictions)
        - delete existing license periods on existing subs (date restrictions apply)
        - update existing license periods on existing subs (must still respect all restrictions)
        - create restrictions on new and existing subscriptions
        - delete restrictions on an existing subscription

        Also tests that deleting a subscription successfully deletes associated objects.
        """

        # create subscription to be deleted with referencing objects to be implicitly deleted
        to_be_deleted_subscription = subscription_factory(contract=contract, product=product)
        tbd_sub_lp = license_period_factory(subscription=to_be_deleted_subscription)
        tbd_sub_gr = geography_restriction_factory(subscription=to_be_deleted_subscription)

        # create subscription to be updated
        preexisting_subscription = subscription_factory(contract=contract, product=product)

        # create license periods to be explicitly deleted and updated
        to_be_deleted_lp = license_period_factory(subscription=preexisting_subscription)
        preexisting_lp = license_period_factory(
            subscription=preexisting_subscription, start_date=date(2021, 1, 1), end_date=date(2022, 1, 31)
        )
        assert LicensePeriod.objects.filter(subscription=preexisting_subscription).count() == 2

        # create existing restrictions and restriction-creating ids:
        # - cov grp restriction already exists + continues to exist
        # - create employer department restriction in request
        # - delete geography restriction in request
        cov_grp_restriction = coverage_group_restriction_factory(subscription=preexisting_subscription)
        tbd_dept_r = department_restriction_factory(subscription=preexisting_subscription)
        geography_restriction_factory(subscription=preexisting_subscription)
        employer_department = tbd_dept_r.employer_department
        tbd_dept_r.delete()

        assert CoverageGroupRestriction.objects.filter(subscription=preexisting_subscription).count() == 1
        assert DepartmentRestriction.objects.filter(subscription=preexisting_subscription).count() == 0
        assert GeographyRestriction.objects.filter(subscription=preexisting_subscription).count() == 1

        data = deepcopy(contract_patch_data)

        # set product on new subscription data
        data["subscriptions"][0]["productId"] = product.pk

        # set subscription to be deleted
        data["subscriptions"].append({"subscriptionId": to_be_deleted_subscription.id, "delete": True})

        # set up new license period data for updated subscription
        new_lp_data = deepcopy(enterprise_license_period_post_data)
        next_start_date: date = preexisting_lp.end_date + timedelta(days=1)
        new_lp_data["start_date"] = next_start_date.isoformat()
        new_lp_data["end_date"] = (next_start_date + timedelta(days=30)).isoformat()

        # set up update subscription data: create, update, delete license periods + restrictions
        patch_sub_data = deepcopy(subscription_patch_data)
        patch_sub_data["subscriptionId"] = preexisting_subscription.id
        patch_sub_data["licensePeriods"].append({"licensePeriodId": preexisting_lp.id, "price": "12.00"})
        patch_sub_data["licensePeriods"].append({"licensePeriodId": to_be_deleted_lp.id, "delete": True})
        patch_sub_data["licensePeriods"].append(new_lp_data)
        patch_sub_data["restrictions"] = {
            "employerCoverageGroupIds": [cov_grp_restriction.employer_coverage_group.id],
            "employerDepartmentIds": [employer_department.id],
            "employerGeographyIds": [],
        }
        data["subscriptions"].append(patch_sub_data)

        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.id)

        print(json.dumps(data, indent=4))
        print(json.dumps(json.loads(response.content), indent=4))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["subscriptions"]) == 3  # 3 instead of 2: gr factory implicitly creates subscription

        # test can delete subscription with existing dependent objects
        assert Subscription.objects.filter(id=to_be_deleted_subscription.id).count() == 0
        assert GeographyRestriction.objects.filter(id=tbd_sub_gr.id).count() == 0
        assert LicensePeriod.objects.filter(id=tbd_sub_lp.id).count() == 0

        # test can delete license period on updated subscription
        assert LicensePeriod.objects.filter(id=to_be_deleted_lp.id).count() == 0

        # test that new restrictions are created and deleted
        assert CoverageGroupRestriction.objects.filter(subscription=preexisting_subscription).count() == 1
        assert DepartmentRestriction.objects.filter(subscription=preexisting_subscription).count() == 1
        assert GeographyRestriction.objects.filter(subscription=preexisting_subscription).count() == 0

        # test price can be updated on updated license period
        assert LicensePeriod.objects.filter(id=preexisting_lp.id).first().price != preexisting_lp.price

    def test_patch_cannot_update_supplier(
        self, user: User, contract: Contract, supplier_factory: TypeSupplierFactory
    ) -> None:
        new_supplier = supplier_factory(name="Anti Cheese Puff Coalition")
        data = {"supplierId": new_supplier.id}
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.id)
        print(response.data, response.status_code)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["supplier"]["id"] != new_supplier.id

    def test_patch_cannot_update_subscription_product(
        self,
        user: User,
        contract: Contract,
        subscription: Subscription,
        product_factory: TypeProductFactory,
    ) -> None:
        new_product = product_factory()
        data = {"subscriptions": [{"subscriptionId": subscription.id, "productId": new_product.id}]}
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["subscriptions"][0]["product"]["id"] != new_product.id

    def test_patch_delete_license_period_does_not_exist(
        self, user: User, contract: Contract, subscription: Subscription
    ) -> None:
        data = {
            "subscriptions": [
                {
                    "subscriptionId": subscription.id,
                    "licensePeriods": [{"licensePeriodId": 69, "delete": True}],
                }
            ]
        }
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.id)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        print(response.data)
        assert response.data["subscriptions"][0]["licensePeriods"][0]["licensePeriodId"][0] == ErrorDetail(
            'Invalid pk "69" - object does not exist.',
            code="does_not_exist",
        )

    def test_patch_update_license_period_does_not_exist(
        self, user: User, contract: Contract, subscription: Subscription
    ) -> None:
        data = {
            "subscriptions": [
                {
                    "subscriptionId": subscription.id,
                    "licensePeriods": [{"licensePeriodId": 69, "price": "9.00"}],
                }
            ]
        }
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.id)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        print(response.data)
        assert response.data["subscriptions"][0]["licensePeriods"][0]["licensePeriodId"][0] == ErrorDetail(
            'Invalid pk "69" - object does not exist.',
            code="does_not_exist",
        )

    def test_patch_delete_subscription_does_not_exist(self, user: User, contract: Contract) -> None:
        data = {"subscriptions": [{"subscriptionId": 69, "delete": True}]}
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.id)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        print(response.data)
        assert response.data["subscriptions"][0]["subscriptionId"][0] == ErrorDetail(
            'Invalid pk "69" - object does not exist.',
            code="does_not_exist",
        )

    def test_patch_update_subscription_does_not_exist(self, user: User, contract: Contract) -> None:
        data = {"subscriptions": [{"subscriptionId": 69, "name": "I am imagined"}]}
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.id)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        print(response.data)
        assert response.data["subscriptions"][0]["subscriptionId"][0] == ErrorDetail(
            'Invalid pk "69" - object does not exist.',
            code="does_not_exist",
        )

    @pytest.mark.parametrize(
        "restriction_key", ["employerCoverageGroupIds", "employerDepartmentIds", "employerGeographyIds"]
    )
    def test_patch_restrictions_employer_mapping_does_not_exist(
        self, user: User, contract: Contract, subscription: Subscription, restriction_key: str
    ) -> None:
        data = {"subscriptions": [{"subscriptionId": subscription.id, "restrictions": {restriction_key: [69]}}]}
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.id)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        print(response.data)
        assert response.data["subscriptions"][0]["restrictions"][restriction_key][0] == ErrorDetail(
            'Invalid pk "69" - object does not exist.',
            code="does_not_exist",
        )

    def test_patch_create_subscription_with_pos_geographies(
        self, user: User, contract: Contract, geography: Geography, product: Product
    ) -> None:
        sub_data = deepcopy(subscription_post_data)
        sub_data["productId"] = product.pk
        sub_data["posGeographyIds"] = [geography.id]
        data = {"subscriptions": [sub_data]}
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.pk)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["subscriptions"][0]["posGeographies"]) == 1

    def test_patch_subscription_create_pos_geographies(
        self,
        user: User,
        contract: Contract,
        subscription: Subscription,
        geography_factory: TypeGeographyFactory,
    ) -> None:
        data = {
            "subscriptions": [
                {
                    "subscriptionId": subscription.id,
                    "posGeographyIds": [
                        geography_factory(name="Lithuania").id,
                        geography_factory(name="Georgia").id,
                    ],
                }
            ]
        }
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.pk)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK, response.data
        assert len(response.data["subscriptions"][0]["posGeographies"]) == 2, response.data["subscriptions"][0][
            "posGeographies"
        ]

    def test_patch_subscription_maintain_pos_geographies(
        self,
        user: User,
        contract: Contract,
        subscription: Subscription,
        subscription_pos_geography_factory: TypeSubscriptionPOSGeographyFactory,
    ) -> None:
        spg = subscription_pos_geography_factory()
        data = {
            "subscriptions": [
                {
                    "subscriptionId": subscription.id,
                    "posGeographyIds": [spg.geography.id],
                }
            ]
        }
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.pk)
        assert response.status_code == status.HTTP_200_OK, response.data
        assert len(response.data["subscriptions"][0]["posGeographies"]) == 1
        assert response.data["subscriptions"][0]["posGeographies"][0]["geography"]["id"] == spg.geography.id

    def test_patch_subscription_delete_pos_geographies(
        self,
        user: User,
        contract: Contract,
        subscription: Subscription,
        subscription_pos_geography_factory: TypeSubscriptionPOSGeographyFactory,
    ) -> None:
        subscription_pos_geography_factory()
        data = {
            "subscriptions": [
                {
                    "subscriptionId": subscription.id,
                    "posGeographyIds": [],
                }
            ]
        }
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.pk)
        assert response.status_code == status.HTTP_200_OK, response.data
        assert len(response.data["subscriptions"][0]["posGeographies"]) == 0

    def test_patch_leading_null_start_date_invalid(
        self, user: User, contract: Contract, subscription: Subscription
    ) -> None:
        new_lp_data = deepcopy(enterprise_license_period_post_data)
        del new_lp_data["startDate"]
        data = {"subscriptions": [{"subscriptionId": subscription.id, "licensePeriods": [new_lp_data]}]}
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.id)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        print(response.data)
        assert response.data["subscriptions"][0]["licensePeriods"][0]["startDate"][0] == ErrorDetail(
            "This field is required.", code="required"
        )

    def test_patch_updated_license_period_gap_invalid(
        self, user: User, contract: Contract, subscription: Subscription
    ) -> None:
        new_lp_data = deepcopy(enterprise_license_period_post_data)
        del new_lp_data["startDate"]
        data = {
            "subscriptions": [
                {
                    "subscriptionId": subscription.id,
                    "licensePeriods": [
                        enterprise_license_period_post_data,
                        new_lp_data,  # this null startDate is now valid
                        enterprise_license_period_post_data,
                    ],
                }
            ]
        }
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.id)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        print(response.data)
        assert response.data["subscriptions"][0]["licensePeriods"][2]["startDate"][0] == ErrorDetail(
            "Start date must be one day after previous license period end date.", code="invalid"
        )

    def test_patch_license_period_type_restrictions_apply(self, user: User, subscription: Subscription) -> None:
        # note: using license period factory causes 200 status code because max_users gets set on model
        license_period = LicensePeriod.objects.create(
            subscription=subscription,
            type=LICENSE_PERIOD_TYPE_ENTERPRISE,
            price=Money(100, "USD"),
            start_date=date(2021, 1, 1),
            end_date=date(2022, 1, 1),
        )
        data = {
            "subscriptions": [
                {
                    "subscriptionId": license_period.subscription.id,
                    "licensePeriods": [{"licensePeriodId": license_period.id, "type": LICENSE_PERIOD_TYPE_USER_LIMIT}],
                }
            ]
        }
        response = contracts_test_resource.request(
            "partial_update", user, data=json.dumps(data), pk=license_period.subscription.contract.id
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        print(response.data)
        assert response.data["subscriptions"][0]["licensePeriods"][0]["maxUsers"][0] == ErrorDetail(
            "This field is required.", code="required"
        )

    def test_patch_previous_contract_validate_graph_cycle_self_reference(
        self,
        user: User,
        contract: Contract,
    ) -> None:
        data = {"previousContractId": contract.id}
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract.id)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data
        assert response.data["previousContractId"][0] == ErrorDetail(string=ERR_MSG_RENEWAL_CYCLE, code="invalid")

    def test_patch_previous_contract_validate_graph_cycle(
        self,
        user: User,
        contract_factory: TypeContractFactory,
    ) -> None:
        contract_a: Contract = contract_factory()
        contract_b: Contract = contract_factory(previous_contract=contract_a)

        # tries to make contract A's previous contract to be B, which is invalid
        data = {"previousContractId": contract_b.id}
        response = contracts_test_resource.request("partial_update", user, data=json.dumps(data), pk=contract_a.id)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data
        assert response.data["previousContractId"][0] == ErrorDetail(string=ERR_MSG_RENEWAL_CYCLE, code="invalid")

    def test_patch_single_license_period_currency(self, user: User, subscription: Subscription) -> None:
        license_period = LicensePeriod.objects.create(
            subscription=subscription,
            type=LICENSE_PERIOD_TYPE_ENTERPRISE,
            price=Money(100, "USD"),
            start_date=date(2021, 1, 1),
            end_date=date(2022, 1, 1),
        )
        data = {
            "subscriptions": [
                {
                    "subscriptionId": subscription.id,
                    "licensePeriods": [
                        {
                            "licensePeriodId": license_period.id,
                            "priceCurrency": "EUR",
                        }
                    ],
                }
            ]
        }
        response = contracts_test_resource.request(
            "partial_update", user, json.dumps(data), pk=subscription.contract.id
        )
        print(response.data)
        assert response.status_code == status.HTTP_200_OK, response.data

    def test_patch_all_multiple_license_period_currencies(self, user: User, subscription: Subscription) -> None:
        lp1 = LicensePeriod.objects.create(
            subscription=subscription,
            type=LICENSE_PERIOD_TYPE_ENTERPRISE,
            price=Money(100, "USD"),
            start_date=date(2021, 1, 1),
            end_date=date(2022, 1, 1),
        )
        lp2 = LicensePeriod.objects.create(
            subscription=subscription,
            type=LICENSE_PERIOD_TYPE_ENTERPRISE,
            price=Money(100, "USD"),
            start_date=date(2022, 1, 2),
            end_date=date(2023, 1, 1),
        )
        data = {
            "subscriptions": [
                {
                    "subscriptionId": subscription.id,
                    "licensePeriods": [
                        {
                            "licensePeriodId": lp1.id,
                            "priceCurrency": "EUR",
                        },
                        {
                            "licensePeriodId": lp2.id,
                            "priceCurrency": "EUR",
                        },
                    ],
                }
            ]
        }
        response = contracts_test_resource.request(
            "partial_update", user, json.dumps(data), pk=subscription.contract.id
        )
        print(response.data)
        assert response.status_code == status.HTTP_200_OK, response.data

    def test_patch_only_some_license_period_currencies_in_subscription(
        self, user: User, subscription: Subscription
    ) -> None:
        lp1 = LicensePeriod.objects.create(
            subscription=subscription,
            type=LICENSE_PERIOD_TYPE_ENTERPRISE,
            price=Money(100, "USD"),
            start_date=date(2021, 1, 1),
            end_date=date(2022, 1, 1),
        )
        lp2 = LicensePeriod.objects.create(
            subscription=subscription,
            type=LICENSE_PERIOD_TYPE_ENTERPRISE,
            price=Money(100, "USD"),
            start_date=date(2022, 1, 2),
            end_date=date(2023, 1, 1),
        )
        data = {
            "subscriptions": [
                {
                    "subscriptionId": subscription.id,
                    "licensePeriods": [
                        {
                            "licensePeriodId": lp1.id,
                            "priceCurrency": "EUR",
                        },
                        {"licensePeriodId": lp2.id},
                    ],
                }
            ]
        }
        response = contracts_test_resource.request(
            "partial_update", user, json.dumps(data), pk=subscription.contract.id
        )
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data
        assert response.data["non_field_errors"][0] == ErrorDetail(
            string="All license period currencies on contract must be the same.",
            code="invalid",
        )
