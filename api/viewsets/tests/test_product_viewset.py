from copy import deepcopy
import json
from typing import Any, Dict, List

import pytest
from rest_framework import exceptions, status

from api.constants import DOMAIN_MARKET_DATA, DOMAIN_TECHNOLOGY
from api.models import Industry, Product, ProductType, Supplier, User, AgreementType, Geography
from api.models.fixtures import TypeProductFactory, TypeSupplierFactory
from api.serializers import ProductSerializer
from api.viewsets import ProductViewSet
from api.viewsets.ProductViewSet import column_name_mappings
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource


products_test_resource = ViewSetTestResource(ProductViewSet, "products-list")


product_post_data: Dict[str, Any] = {
    "name": "GOOD PRODUCT",
    "description": "A good product",
    "domain": 1,
    "status": 1,
    "supplierId": 1,
    "industryIds": [3, 4],
    "geographyIds": [2, 3],
    "typeIds": [1],
    "agreementTypeId": 1,
    "startDate": "2020-01-01",
    "endDate": "2020-12-31",
    "url": "https://www.goodproduct.com",
}


class TestProductModelPermissions:
    @pytest.mark.django_db
    def test_products_will_prevent_get_one(self, product: Product, supplier_user_with_no_permissions: User) -> None:
        response = products_test_resource.request(
            "retrieve",
            force_auth_user=supplier_user_with_no_permissions,
            pk=product.id,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_products_will_prevent_get_list(self, supplier_user_with_no_permissions: User) -> None:
        response = products_test_resource.request("list", supplier_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_products_will_prevent_post(self, supplier_user_with_no_permissions: User) -> None:
        response = products_test_resource.request("create", supplier_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_products_will_prevent_delete(self, product: Product, supplier_user_with_no_permissions: User) -> None:
        response = products_test_resource.request("destroy", supplier_user_with_no_permissions, pk=product.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_products_will_prevent_patch(self, product: Product, supplier_user_with_no_permissions: User) -> None:
        response = products_test_resource.request(
            "partial_update",
            force_auth_user=supplier_user_with_no_permissions,
            pk=product.id,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_products_will_prevent_put(self, product: Product, supplier_user_with_no_permissions: User) -> None:
        response = products_test_resource.request(
            "update",
            force_auth_user=supplier_user_with_no_permissions,
            pk=product.pk,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestProductTenancy:
    @pytest.mark.django_db
    def test_products_get_will_return_correct_products(
        self,
        product_factory: TypeProductFactory,
        suppliers: List[Supplier],
        supplier_user: User,
    ) -> None:
        # create relevant products
        products = [
            product_factory(name=f"product_{supplier.employer.name}", supplier=supplier) for supplier in suppliers
        ]
        products.append(product_factory(name="product_1", supplier=supplier_user.person.employer.supplier))

        response = products_test_resource.request("list", supplier_user)
        print(products)
        print(response.data)
        assert response.data["count"] == len(products)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_products_post_will_create_correct_products(
        self,
        industries: List[Industry],
        agreements_types: List[AgreementType],
        geographies: List[Geography],
        supplier_user: User,
    ) -> None:
        data = deepcopy(product_post_data)
        data.update({"supplierId": supplier_user.person.employer.supplier.id})
        response = products_test_resource.request("create", supplier_user, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get("supplier").get("id") == supplier_user.person.employer.supplier.id

    @pytest.mark.django_db
    def test_products_post_will_not_create_incorrect_products(
        self, industries: List[Industry], supplier_user: User
    ) -> None:
        data = deepcopy(product_post_data)
        data.update({"supplierId": supplier_user.person.employer.supplier.id + 1})
        response = products_test_resource.request("create", supplier_user, json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # Uncomment below when Product has edit / patch capabilities
    """
    @pytest.mark.django_db
    def test_products_patch_will_not_update_forbidden_products(
        self, buyer: Buyer, supplier_user: User, industries: List[Industry]
    ) -> None:
        url = reverse("products-list")
        view = ProductViewSet.ascategoriesIRequestFactory()
        data = deepcopy(buyer_patch_data)
        request = request_factory.patch(
            url,
            data=json.dumps(data),
            content_type="application/json",
            kwargs={"pk": buyer.pk},
        )
        force_authenticate(request, user=supplier_user)
        response = view(request, pk=buyer.pk)
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    """

    @pytest.mark.django_db
    def test_products_delete_will_not_delete_forbidden_products(
        self, product_factory: TypeProductFactory, suppliers: List[Supplier], supplier_user: User
    ) -> None:
        product = product_factory(name=f"product_{suppliers[0].employer.name}", supplier=suppliers[0])
        response = products_test_resource.request("destroy", supplier_user, pk=product.pk)
        print(response.data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetProduct:
    @pytest.mark.django_db
    def test_api_can_list_products(self, product_factory: TypeProductFactory, user: User) -> None:
        """Test that we can list products"""
        # Create three products
        product_factory()
        product_factory()
        product_factory()

        response = products_test_resource.request("list", user)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    @pytest.mark.django_db
    def test_api_can_list_products_filtered_by_supplier_id(
        self,
        product_factory: TypeProductFactory,
        supplier_factory: TypeSupplierFactory,
        user: User,
    ) -> None:
        # Create two products, each belonging to a different supplier
        supplier_1 = supplier_factory()
        supplier_2 = supplier_factory()
        product_1 = product_factory(supplier=supplier_1)
        product_factory(supplier=supplier_2)

        response = products_test_resource.request("list", user, data={"supplierId": supplier_1.pk})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == product_1.pk

    @pytest.mark.django_db
    def test_api_can_list_products_filtered_by_domain_id(
        self,
        product_factory: TypeProductFactory,
        user: User,
    ) -> None:
        # Create two products, each belonging to a different domain
        product_1 = product_factory(domain=DOMAIN_MARKET_DATA)
        product_factory(domain=DOMAIN_TECHNOLOGY)

        response = products_test_resource.request("list", user, data={"domainId": DOMAIN_MARKET_DATA})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == product_1.pk

    @pytest.mark.django_db
    def test_api_can_fetch_product_by_id(self, product: Product, user: User) -> None:
        """Test that we can fetch a product by ID"""
        response = products_test_resource.request(
            "retrieve",
            user,
            pk=product.pk,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == product.id


@pytest.mark.parametrize(
    "filter_column",
    column_name_mappings.keys(),
)
@pytest.mark.django_db
class TestListProductFilterColumns:
    def test_column_mappings_valid(self, user: User, filter_column: str, product: Product) -> None:
        response = products_test_resource.request(
            "list", user, data={"filterContent": f"{filter_column} equals '1'", "filterOperator": "and"}
        )
        assert response.status_code == status.HTTP_200_OK, response.data


class TestProductCreation:
    @pytest.mark.django_db
    def test_api_can_create_product(
        self,
        user: User,
        industries: List[Industry],
        supplier_with_id_1: Supplier,
        product_types: List[ProductType],
        agreements_types: List[AgreementType],
        geographies: List[Geography],
    ) -> None:
        """Test that we can create a product"""
        response = products_test_resource.request("create", user, json.dumps(product_post_data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get("name") == product_post_data.get("name")

    @pytest.mark.django_db
    @pytest.mark.parametrize("domain", [1, 2, 3, 4])
    def test_create_product_with_valid_domains(
        self,
        domain: int,
        user: User,
        industries: List[Industry],
        supplier_with_id_1: Supplier,
        product_types: List[ProductType],
        agreements_types: List[AgreementType],
        geographies: List[Geography],
    ) -> None:
        data = deepcopy(product_post_data)
        data.update({"domain": domain})
        response = products_test_resource.request("create", user, json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get("domain").get("id") == domain

    @pytest.mark.django_db
    def test_create_product_with_invalid_domain(
        self,
        user: User,
    ) -> None:
        invalid_domain: int = 5
        data = deepcopy(product_post_data)
        data.update({"domain": invalid_domain})
        response = products_test_resource.request("create", user, json.dumps(data))

        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("domain") == [
            exceptions.ErrorDetail(f'"{invalid_domain}" is not a valid choice.', code="invalid_choice")
        ]

    @pytest.mark.django_db
    def test_create_product_with_invalid_agreement_type(
        self, user: User, industries: List[Industry], agreements_types: List[AgreementType]
    ) -> None:
        invalid_agreement_type: int = 100
        data = deepcopy(product_post_data)
        data.update({"agreementTypeId": invalid_agreement_type})
        response = products_test_resource.request("create", user, json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("agreementTypeId") == [
            exceptions.ErrorDetail(
                f'Invalid pk "{invalid_agreement_type}" - object does not exist.', code="does_not_exist"
            )
        ]


class TestDateValidation:
    @pytest.mark.django_db
    def test_post_products_with_mmddyyyy_dates(
        self,
        user: User,
        industries: List[Industry],
        supplier_with_id_1: Supplier,
        product_types: List[ProductType],
    ) -> None:

        data = deepcopy(product_post_data)
        data["startDate"] = "01-01-2020"
        response = products_test_resource.request("create", user, json.dumps(data))

        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("startDate")[0] == exceptions.ErrorDetail(
            "Date has wrong format. Use one of these formats instead: YYYY-MM-DD.", code="invalid"
        )


class TestNonRequiredFields:
    @pytest.mark.django_db
    def test_post_products_url_is_optional(
        self,
        user: User,
        industries: List[Industry],
        agreements_types: List[AgreementType],
        geographies: List[Geography],
        supplier_with_id_1: Supplier,
    ) -> None:
        data = deepcopy(product_post_data)
        del data["url"]
        response = products_test_resource.request("create", user, json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_post_products_agreement_type_is_optional(
        self,
        user: User,
        industries: List[Industry],
        agreements_types: List[AgreementType],
        geographies: List[Geography],
        supplier_with_id_1: Supplier,
    ) -> None:
        data = deepcopy(product_post_data)
        del data["agreementTypeId"]
        response = products_test_resource.request("create", user, json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED


class TestFieldNameValidation:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "required_field",
        [key for key, value in ProductSerializer().get_fields().items() if value.required],
    )
    def test_post_products_validates_required_top_level_product_fields(
        self,
        user: User,
        industries: List[Industry],
        supplier_with_id_1: Supplier,
        required_field: str,
    ) -> None:
        """Test that wee will get an error when misnaming a top-level field that is required for Product creation"""
        data = deepcopy(product_post_data)
        data[required_field + "1"] = data.pop(required_field)
        response = products_test_resource.request("create", user, json.dumps(data))

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get(required_field)[0] == exceptions.ErrorDetail(
            "This field is required.", code="required"
        )

    @pytest.mark.django_db
    def test_post_products_validates_bad_industry_id(
        self, user: User, industries: List[Industry], supplier_with_id_1: Supplier
    ) -> None:
        """Test that we will get an error when providing a bad industry ID"""
        data = deepcopy(product_post_data)
        data["industryIds"] = [69]
        response = products_test_resource.request("create", user, json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("industryIds")[0] == exceptions.ErrorDetail(
            'Invalid pk "69" - object does not exist.', code="does_not_exist"
        )

    @pytest.mark.django_db
    def test_post_products_validates_bad_product_type_id(
        self, user: User, industries: List[Industry], supplier_with_id_1: Supplier, product_types: List[ProductType]
    ) -> None:
        """Test that we will get an error when providing a bad type ID"""
        data = deepcopy(product_post_data)
        data["typeIds"] = [69]
        response = products_test_resource.request("create", user, json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["typeIds"][0] == exceptions.ErrorDetail(
            'Invalid pk "69" - object does not exist.', code="does_not_exist"
        )


class TestForeignKeys:
    @pytest.mark.django_db
    def test_post_products_validates_bad_supplier_id(
        self, user: User, industries: List[Industry], supplier_with_id_1: Supplier
    ) -> None:
        """Test that we will get an error when providing a bad supplier ID"""
        data = deepcopy(product_post_data)
        data["supplierId"] = 69
        response = products_test_resource.request("create", user, json.dumps(data))

        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("supplierId")[0] == exceptions.ErrorDetail(
            'Invalid pk "69" - object does not exist.', code="does_not_exist"
        )

    @pytest.mark.django_db
    def test_post_products_validates_bad_agreement_type_id(
        self, user: User, industries: List[Industry], supplier_with_id_1: Supplier
    ) -> None:
        """Test that we will get an error when providing a bad agreement type ID"""
        data = deepcopy(product_post_data)
        data["agreementTypeId"] = 69
        response = products_test_resource.request("create", user, json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("agreementTypeId")[0] == exceptions.ErrorDetail(
            'Invalid pk "69" - object does not exist.', code="does_not_exist"
        )
