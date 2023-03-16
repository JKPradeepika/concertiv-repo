from copy import deepcopy
import json
from typing import Any, Dict, List

import pytest
from rest_framework import exceptions, status

from api.models.Buyer import Buyer
from api.models.Industry import Industry
from api.models.Geography import Geography
from api.models.User import User
from api.models.fixtures import TypeBuyerFactory
from api.serializers import AddressSerializer, BuyerSerializer
from api.viewsets import BuyerViewSet
from api.viewsets.BuyerViewSet import column_name_mappings
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource


buyers_test_resource = ViewSetTestResource(BuyerViewSet, "buyers-list")


buyer_post_data: Dict[str, Any] = {
    "name": "Concertiv, Inc.",
    "shortName": "TEST",
    "shortCode": "TEST",
    "accountStatus": 1,
    "industryIds": [3, 4],
    "geographyIds": [2, 3],
    "businessType": {"id": 1, "name": "Fake Business Type"},
    "firstJoinedAt": "2022-04-01",
    "terminationDate": "2023-04-01",
    "savingsReportFrequencyInMonths": 3,
    "addresses": [
        {
            "street1": "123 Test Walks",
            "street2": "123",
            "city": "Elden",
            "state": "Ring",
            "country": "United States",
            "postalCode": "30097",
            "isPrimary": True,
        }
    ],
}


buyer_patch_data = deepcopy(buyer_post_data)
# Addresses cannot currently be updated via `PATCH /api/buyers``
del buyer_patch_data["addresses"]


class TestBuyerModelPermissions:
    @pytest.mark.django_db
    def test_buyers_will_prevent_get_one(self, concertiv_user_with_no_permissions: User) -> None:
        response = buyers_test_resource.request(
            "retrieve",
            force_auth_user=concertiv_user_with_no_permissions,
            pk=concertiv_user_with_no_permissions.person.employer.buyer.id,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_buyers_will_prevent_get_list(self, concertiv_user_with_no_permissions: User) -> None:
        response = buyers_test_resource.request(
            "list",
            force_auth_user=concertiv_user_with_no_permissions,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_buyers_will_prevent_post(self, concertiv_user_with_no_permissions: User) -> None:
        response = buyers_test_resource.request("create", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_buyers_will_prevent_delete(self, buyer: Buyer, concertiv_user_with_no_permissions: User) -> None:
        response = buyers_test_resource.request(
            "destroy",
            force_auth_user=concertiv_user_with_no_permissions,
            pk=concertiv_user_with_no_permissions.person.employer.buyer.pk,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_buyers_will_prevent_patch(self, buyer: Buyer, concertiv_user_with_no_permissions: User) -> None:
        response = buyers_test_resource.request(
            "partial_update",
            force_auth_user=concertiv_user_with_no_permissions,
            pk=concertiv_user_with_no_permissions.person.employer.buyer.pk,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_buyers_will_prevent_put(self, concertiv_user_with_no_permissions: User) -> None:
        response = buyers_test_resource.request(
            "update",
            force_auth_user=concertiv_user_with_no_permissions,
            pk=concertiv_user_with_no_permissions.person.employer.buyer.pk,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestBuyerTenancy:
    @pytest.mark.django_db
    def test_buyers_get_one_will_return_correct_company(
        self, buyer_factory: TypeBuyerFactory, user_with_other_buyer: User
    ) -> None:
        buyer = user_with_other_buyer.person.employer.buyer
        response = buyers_test_resource.request("retrieve", user_with_other_buyer, pk=buyer.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == buyer.id

    @pytest.mark.django_db
    def test_buyers_get_one_will_not_return_bad_company(self, buyer: Buyer, user_with_other_buyer: User) -> None:
        response = buyers_test_resource.request("retrieve", user_with_other_buyer, pk=buyer.id)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_buyers_get_will_return_correct_companies(self, buyers: List[Buyer], user_with_other_buyer: User) -> None:
        response = buyers_test_resource.request("list", user_with_other_buyer)
        print(response.data)
        assert response.data["count"] != 0
        for result in response.data["results"]:
            assert result["id"] == user_with_other_buyer.person.employer.buyer.id
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_buyers_post_will_prevent_external_user(self, user_with_other_buyer: User) -> None:
        response = buyers_test_resource.request(
            "create",
            user_with_other_buyer,
            data=json.dumps(buyer_post_data),
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_buyers_put_will_not_update_forbidden_buyes(self) -> None:
        pass

    @pytest.mark.django_db
    def test_buyers_patch_will_not_update_forbidden_buyers(
        self, buyer: Buyer, user_with_other_buyer: User, industries: List[Industry]
    ) -> None:
        response = buyers_test_resource.request(
            "partial_update",
            user_with_other_buyer,
            data=json.dumps(buyer_patch_data),
            pk=buyer.pk,
        )
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_buyers_delete_will_not_delete_forbidden_buyers(
        self, buyer: Buyer, user_with_other_buyer: User, industries: List[Industry]
    ) -> None:
        response = buyers_test_resource.request("destroy", user_with_other_buyer, pk=buyer.pk)
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetBuyer:
    @pytest.mark.django_db
    def test_api_can_list_buyers(self, buyer: Buyer, user: User) -> None:
        """Test that we can list buyers"""
        response = buyers_test_resource.request("list", user)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == buyer.pk

    @pytest.mark.django_db
    def test_api_can_fetch_buyer_by_id(self, buyer: Buyer, user: User) -> None:
        """Test that we can fetch a buyer by ID"""
        response = buyers_test_resource.request("retrieve", user, pk=buyer.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == buyer.id


@pytest.mark.parametrize(
    "filter_column",
    column_name_mappings.keys(),
)
@pytest.mark.django_db
class TestListBuyerFilterColumns:
    def test_column_mappings_valid(self, user: User, filter_column: str, buyer: Buyer) -> None:
        response = buyers_test_resource.request(
            "list", user, data={"filterContent": f"{filter_column} equals '1'", "filterOperator": "and"}
        )
        assert response.status_code == status.HTTP_200_OK, response.data


class TestPostBuyer:
    @pytest.mark.django_db
    def test_api_can_create_buyer(
        self,
        user: User,
        industries: List[Industry],
        geographies: List[Geography],
    ) -> None:
        """Test that we can create a buyer"""
        response = buyers_test_resource.request("create", user, data=json.dumps(buyer_post_data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get("shortName") == "TEST"

    @pytest.mark.django_db
    def test_post_buyers_validates_that_the_short_code_is_unique(
        self, user: User, buyer: Buyer, industries: List[Industry], geographies: List[Geography]
    ) -> None:
        """Test that we will get an error when duplicating a short code"""
        data = deepcopy(buyer_post_data)
        data["shortCode"] = buyer.short_code
        response = buyers_test_resource.request("create", user, data=json.dumps(data))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("shortCode") == [
            exceptions.ErrorDetail("This client code already exists.", code="unique")
        ]

    @pytest.mark.django_db
    def test_post_buyers_validates_the_short_code_length(
        self, user: User, industries: List[Industry], geographies: List[Geography]
    ) -> None:
        data = deepcopy(buyer_post_data)
        data["shortCode"] = "A_SHORT_CODE_THAT_IS_WAY_TOO_LONG"
        response = buyers_test_resource.request("create", user, data=json.dumps(data))

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("shortCode") == [
            exceptions.ErrorDetail("Ensure this field has no more than 5 characters.", code="max_length")
        ]


class TestPatchBuyer:
    @pytest.mark.django_db
    def test_api_can_patch_buyer(
        self, buyer: Buyer, user: User, industries: List[Industry], geographies: List[Geography]
    ) -> None:
        response = buyers_test_resource.request(
            "partial_update",
            user,
            data=json.dumps(buyer_patch_data),
            pk=buyer.pk,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("name") == buyer_patch_data["name"]
        assert response.data.get("shortName") == buyer_patch_data["shortName"]
        assert response.data.get("shortCode") == buyer_patch_data["shortCode"]
        assert response.data.get("accountStatus").get("id") == buyer_patch_data["accountStatus"]
        assert response.data.get("firstJoinedAt") == buyer_patch_data["firstJoinedAt"]
        assert response.data.get("savingsReportFrequencyInMonths") == buyer_patch_data["savingsReportFrequencyInMonths"]
        industry_ids = [industry["id"] for industry in response.data.get("industries")]
        assert industry_ids == buyer_patch_data["industryIds"]

    # This test somewhat duplicates the `test_post_buyers_validates_that_the_short_code_is_unique` test,
    # but the PATCH endpoint previously did not use the same validation logic as the POST endpoint and was
    # therefore not validating that the `short_code` was unique, so we're keeping this test as a regression test.
    @pytest.mark.django_db
    def test_patch_buyers_validates_that_the_short_code_is_unique(
        self,
        buyer: Buyer,
        buyer_factory: TypeBuyerFactory,
        industries: List[Industry],
        geographies: List[Geography],
        user: User,
    ) -> None:
        buyer_factory(short_code="TAKEN")
        data = deepcopy(buyer_patch_data)
        data["shortCode"] = "TAKEN"
        response = buyers_test_resource.request("partial_update", user, data=json.dumps(data), pk=buyer.pk)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("shortCode") == [
            exceptions.ErrorDetail("This client code already exists.", code="unique")
        ]


class TestFieldNameValidation:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "required_field", [key for key, value in BuyerSerializer().get_fields().items() if value.required]
    )
    def test_post_buyers_validates_required_top_level_buyer_fields(
        self,
        user: User,
        industries: List[Industry],
        geographies: List[Geography],
        required_field: str,
    ) -> None:
        """Test that we will get an error when misnaming a top-level field that is required for Buyer creation"""
        data = deepcopy(buyer_post_data)
        data[required_field + "1"] = data.pop(required_field)
        response = buyers_test_resource.request("create", user, data=json.dumps(data))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get(required_field)[0] == exceptions.ErrorDetail(
            "This field is required.", code="required"
        )

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "required_field", [key for key, value in AddressSerializer().get_fields().items() if value.required]
    )
    def test_api_validates_address_info(
        self, user: User, industries: List[Industry], geographies: List[Geography], required_field: str
    ) -> None:
        """Test that we will get an error when misnaming an address field that is required for Buyer creation"""
        data = deepcopy(buyer_post_data)
        data["addresses"][0][required_field + "1"] = data["addresses"][0].pop(required_field)
        response = buyers_test_resource.request("create", user, data=json.dumps(data))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("addresses")[0].get(required_field)[0] == exceptions.ErrorDetail(
            "This field is required.", code="required"
        )


class TestNonRequiredFields:
    @pytest.mark.django_db
    def test_savings_report_frequency_in_months_is_optional(
        self,
        user: User,
        industries: List[Industry],
        geographies: List[Geography],
    ) -> None:
        data = deepcopy(buyer_post_data)
        del data["savingsReportFrequencyInMonths"]
        response = buyers_test_resource.request("create", user, data=json.dumps(data))
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_termination_date_is_optional(
        self,
        user: User,
        industries: List[Industry],
        geographies: List[Geography],
    ) -> None:
        data = deepcopy(buyer_post_data)
        del data["terminationDate"]
        response = buyers_test_resource.request("create", user, data=json.dumps(data))
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_addresses_are_optional(
        self,
        user: User,
        industries: List[Industry],
        geographies: List[Geography],
    ) -> None:
        data = deepcopy(buyer_post_data)
        del data["addresses"]
        response = buyers_test_resource.request("create", user, data=json.dumps(data))
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_business_type_is_optional(
        self,
        user: User,
        industries: List[Industry],
        geographies: List[Geography],
    ) -> None:
        data = deepcopy(buyer_post_data)
        del data["businessType"]
        response = buyers_test_resource.request("create", user, data=json.dumps(data))
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_non_required_address_fields(
        self,
        user: User,
        industries: List[Industry],
        geographies: List[Geography],
    ) -> None:
        """Test non-required fields address fields will still return a success"""
        data = deepcopy(buyer_post_data)
        data["shortCode"] = "TEST2"
        data["addresses"][0].pop("street2")
        response = buyers_test_resource.request("create", user, data=json.dumps(data))
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get("shortCode") == "TEST2"


class TestIndustryErrors:
    @pytest.mark.django_db
    def test_post_buyers_returns_an_error_when_it_receives_a_non_existent_industry(
        self,
        user: User,
        industries: List[Industry],
        geographies: List[Geography],
    ) -> None:
        """Test that we will get an error when posting a non-existent industry"""
        data = deepcopy(buyer_post_data)
        data["industryIds"][0] = 69
        response = buyers_test_resource.request("create", user, data=json.dumps(data))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("industryIds") == [
            exceptions.ErrorDetail(string='Invalid pk "69" - object does not exist.', code="does_not_exist")
        ]

    @pytest.mark.django_db
    def test_post_buyers_validates_that_industries_is_not_null(
        self,
        user: User,
        industries: List[Industry],
        geographies: List[Geography],
    ) -> None:
        data = deepcopy(buyer_post_data)
        del data["industryIds"]
        response = buyers_test_resource.request("create", user, data=json.dumps(data))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("industryIds") == [exceptions.ErrorDetail("This field is required.", code="required")]

    @pytest.mark.django_db
    def test_post_buyers_validates_that_industries_are_not_required(
        self,
        user: User,
        industries: List[Industry],
        geographies: List[Geography],
    ) -> None:
        data = deepcopy(buyer_post_data)
        data["industryIds"] = []
        response = buyers_test_resource.request("create", user, data=json.dumps(data))
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_post_buyers_validates_that_geographies_are_not_required(
        self,
        user: User,
        industries: List[Industry],
        geographies: List[Geography],
    ) -> None:
        data = deepcopy(buyer_post_data)
        data["geographyIds"] = []
        response = buyers_test_resource.request("create", user, data=json.dumps(data))
        assert response.status_code == status.HTTP_201_CREATED


class TestForeignKeys:
    @pytest.mark.django_db
    def test_post_products_validates_bad_agreement_type_id(
        self,
        user: User,
        industries: List[Industry],
        geographies: List[Geography],
    ) -> None:
        """Test that we will get an error when providing a bad business type ID"""
        data = deepcopy(buyer_post_data)
        data["businessTypeId"] = 69
        response = buyers_test_resource.request("create", user, json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("businessTypeId")[0] == exceptions.ErrorDetail(
            'Invalid pk "69" - object does not exist.', code="does_not_exist"
        )
