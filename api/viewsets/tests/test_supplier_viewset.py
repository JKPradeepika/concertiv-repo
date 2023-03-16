import json
from copy import deepcopy
from typing import Any, Dict, List

import pytest
from rest_framework import exceptions, status

from api.constants import (
    DOMAIN_INSURANCE,
    DOMAIN_MARKET_DATA,
    DOMAINS,
    SUPPLIER_TYPE_GENERAL,
    SUPPLIER_TYPE_RESELLER,
)
from api.models import Industry, Supplier, User
from api.models.fixtures import TypeProductFactory, TypeSupplierFactory
from api.serializers import SupplierSerializer
from api.viewsets import SupplierViewSet
from api.viewsets.SupplierViewSet import column_name_mappings
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource

suppliers_test_resource = ViewSetTestResource(SupplierViewSet, "suppliers-list")

supplier_post_data: Dict[str, Any] = {
    "name": "Concertiv, Inc.",
    "description": "TEST",
    "isNdaSigned": True,
    "typeId": 1,
    "url": "https://concertiv.com",
}

supplier_patch_data = deepcopy(supplier_post_data)

content_type_data = "application/json"


class TestSupplierModelPermissions:
    @pytest.mark.django_db
    def test_suppliers_will_prevent_get_one(self, supplier_user_with_no_permissions: User) -> None:
        response = suppliers_test_resource.request(
            "retrieve",
            supplier_user_with_no_permissions,
            pk=supplier_user_with_no_permissions.person.employer.supplier.id,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_suppliers_will_prevent_get_list(self, supplier_user_with_no_permissions: User) -> None:
        response = suppliers_test_resource.request("list", supplier_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_suppliers_will_prevent_post(self, supplier_user_with_no_permissions: User) -> None:
        response = suppliers_test_resource.request("create", supplier_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_suppliers_will_prevent_delete(self, supplier: Supplier, supplier_user_with_no_permissions: User) -> None:
        response = suppliers_test_resource.request(
            "destroy",
            force_auth_user=supplier_user_with_no_permissions,
            pk=supplier_user_with_no_permissions.person.employer.supplier.pk,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_suppliers_will_prevent_patch(self, supplier: Supplier, supplier_user_with_no_permissions: User) -> None:
        response = suppliers_test_resource.request(
            "partial_update",
            force_auth_user=supplier_user_with_no_permissions,
            pk=supplier_user_with_no_permissions.person.employer.supplier.pk,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_suppliers_will_prevent_put(self, supplier_user_with_no_permissions: User) -> None:
        response = suppliers_test_resource.request(
            "update",
            force_auth_user=supplier_user_with_no_permissions,
            pk=supplier_user_with_no_permissions.person.employer.supplier.id,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSupplierTenancy:
    @pytest.mark.django_db
    def test_suppliers_get_one_will_return_correct_company(self, supplier: Supplier, supplier_user: User) -> None:
        response = suppliers_test_resource.request(
            "retrieve",
            force_auth_user=supplier_user,
            pk=supplier.id,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == supplier.id

    @pytest.mark.django_db
    def test_suppliers_get_will_return_correct_companies(self, suppliers: List[Supplier], supplier_user: User) -> None:
        response = suppliers_test_resource.request(
            "list",
            force_auth_user=supplier_user,
        )
        print(response.data)
        assert response.data["count"] == len(Supplier.objects.all())
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_suppliers_post_will_prevent_external_user(self, supplier_user: User) -> None:
        response = suppliers_test_resource.request(
            "create", force_auth_user=supplier_user, data=json.dumps(supplier_post_data)
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_suppliers_patch_will_not_update_forbidden_supplier(
        self, supplier_with_id_1: Supplier, supplier_user: User
    ) -> None:
        response = suppliers_test_resource.request(
            "partial_update",
            force_auth_user=supplier_user,
            data=json.dumps(supplier_patch_data),
            pk=supplier_with_id_1.pk,
        )
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetSupplier:
    @pytest.mark.django_db
    def test_api_can_list_suppliers(self, supplier: Supplier, user: User) -> None:
        """Test that we can list suppliers"""
        response = suppliers_test_resource.request("list", force_auth_user=user)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == supplier.pk

    @pytest.mark.django_db
    def test_supplier_products_have_domain(
        self, user: User, supplier_factory: TypeSupplierFactory, product_factory: TypeProductFactory
    ) -> None:
        selected_supplier = None
        for domain, _ in DOMAINS:
            supplier = supplier_factory()
            product_factory(domain=domain, supplier=supplier)
            if domain == DOMAIN_MARKET_DATA:
                selected_supplier = supplier

        response = suppliers_test_resource.request("list", user, data={"domainId": DOMAIN_MARKET_DATA})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == selected_supplier.pk

    @pytest.mark.django_db
    def test_supplier_contains_products_filter_no_products(self, supplier: Supplier, user: User) -> None:
        response = suppliers_test_resource.request("list", force_auth_user=user, data={"contains_products": True})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

        response = suppliers_test_resource.request("list", force_auth_user=user, data={"contains_products": False})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == supplier.pk

    @pytest.mark.django_db
    def test_supplier_contains_products_filter_with_products(
        self, supplier: Supplier, user: User, product_factory: TypeProductFactory
    ) -> None:
        product_factory(supplier=supplier)
        response = suppliers_test_resource.request("list", force_auth_user=user, data={"contains_products": True})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == supplier.pk

        response = suppliers_test_resource.request("list", force_auth_user=user, data={"contains_products": False})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    @pytest.mark.django_db
    def test_supplier_filter_supplier_type(self, user: User, supplier_factory: TypeSupplierFactory) -> None:
        supplier = supplier_factory(type=SUPPLIER_TYPE_RESELLER)
        supplier_factory(type=SUPPLIER_TYPE_GENERAL)
        response = suppliers_test_resource.request(
            "list", force_auth_user=user, data={"typeId": SUPPLIER_TYPE_RESELLER}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == supplier.pk

    @pytest.mark.django_db
    def test_api_can_fetch_supplier_by_id(self, supplier: Supplier, user: User) -> None:
        """Test that we can fetch a supplier by ID"""
        response = suppliers_test_resource.request("retrieve", user, pk=supplier.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == supplier.id


@pytest.mark.django_db
class TestListSupplierFilterColumns:
    @pytest.mark.parametrize(
        "filter_column",
        column_name_mappings.keys(),
    )
    def test_column_mappings_valid(self, user: User, filter_column: str, supplier: Supplier) -> None:
        response = suppliers_test_resource.request(
            "list", user, data={"filterContent": f"{filter_column} equals '1'", "filterOperator": "and"}
        )
        assert response.status_code == status.HTTP_200_OK, response.data

    def test_filter_content_domains(
        self, user: User, supplier_factory: TypeSupplierFactory, product_factory: TypeProductFactory
    ) -> None:
        product_factory(supplier=supplier_factory(), domain=DOMAIN_MARKET_DATA)
        product_factory(supplier=supplier_factory(), domain=DOMAIN_INSURANCE)

        response = suppliers_test_resource.request(
            "list",
            user,
            url=(
                f"/suppliers?filterContent=domains+equals+%27{DOMAIN_MARKET_DATA}%27"
                f"&filterOperator=and&sortContent=description+asc"
            ),
        )
        print(response.data)
        assert response.status_code == status.HTTP_200_OK, response.data
        assert response.data["count"] == 1, response.data


class TestPostSupplier:
    @pytest.mark.django_db
    def test_api_can_create_supplier(self, user: User, industries: List[Industry]) -> None:
        """Test that we can create a supplier"""
        response = suppliers_test_resource.request("create", force_auth_user=user, data=json.dumps(supplier_post_data))
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get("description") == "TEST"

    @pytest.mark.django_db
    def test_post_suppliers_returns_an_error_when_it_receives_a_non_existent_product_type(
        self,
        user: User,
        industries: List[Industry],
    ) -> None:
        data = deepcopy(supplier_post_data)
        data["typeId"] = 69
        response = suppliers_test_resource.request("create", user, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("typeId")[0] == exceptions.ErrorDetail(
            '"69" is not a valid choice.', code="invalid_choice"
        )


class TestPatchSupplier:
    @pytest.mark.django_db
    def test_api_can_patch_supplier(self, supplier: Supplier, user: User, industries: List[Industry]) -> None:
        response = suppliers_test_resource.request(
            "partial_update",
            force_auth_user=user,
            data=json.dumps(supplier_patch_data),
            pk=supplier.pk,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("name") == supplier_patch_data["name"]
        assert response.data.get("description") == supplier_patch_data["description"]
        assert response.data.get("isNdaSigned") == supplier_patch_data["isNdaSigned"]
        assert response.data.get("type").get("id") == supplier_patch_data["typeId"]
        assert response.data.get("url") == supplier_patch_data["url"]


class TestFieldNameValidation:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "required_field", [key for key, value in SupplierSerializer().get_fields().items() if value.required]
    )
    def test_post_suppliers_validates_required_top_level_supplier_fields(
        self,
        user: User,
        industries: List[Industry],
        required_field: str,
    ) -> None:
        """Test that we will get an error when misnaming a top-level field that is required for Supplier creation"""
        data = deepcopy(supplier_post_data)
        data[required_field + "1"] = data.pop(required_field)
        response = suppliers_test_resource.request(
            "create",
            force_auth_user=user,
            data=json.dumps(data),
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get(required_field)[0] == exceptions.ErrorDetail(
            "This field is required.", code="required"
        )


class TestNonRequiredFields:
    @pytest.mark.django_db
    def test_addresses_are_optional(self, user: User, industries: List[Industry]) -> None:
        response = suppliers_test_resource.request(
            "create",
            force_auth_user=user,
            data=json.dumps(supplier_post_data),
        )
        assert response.status_code == status.HTTP_201_CREATED
