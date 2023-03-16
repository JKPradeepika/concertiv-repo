from typing import Any, Optional
import json
from io import StringIO

import pytest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ErrorDetail

from api.models import AllowedDocumentFileExtension
from api.models import Buyer, Contract, Document, DocumentType, Product, Supplier, User
from api.models.fixtures import (
    TypeBusinessDealFactory,
    TypeBuyerFactory,
    TypeContractFactory,
    TypeDocumentFactory,
    TypeDocumentTypeFactory,
    TypeProductFactory,
    TypeSupplierFactory,
)
from api.viewsets import DocumentViewSet
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource

docs_test_resource = ViewSetTestResource(DocumentViewSet, "documents-list", override_default_storage=True)


def create_test_file(contents: str = "string from a fake file", file_name: Optional[str] = "file.pdf"):
    file = StringIO(contents)
    if file_name:
        file.name = file_name
    return file


@pytest.mark.django_db
class TestListDocuments:
    def test_list_documents(self, user: User, document: Document) -> None:
        response = docs_test_resource.request("list", user)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == document.id
        for key in ["buyer", "contract", "product", "supplier", "updatedAt"]:
            assert key in response.data["results"][0]

    def test_list_documents_no_auth(self) -> None:
        response = docs_test_resource.request("list", force_auth_user=None)
        print(response.data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_filtered_access_buyers(
        self, user_with_other_buyer: User, buyer: Buyer, document_factory: TypeDocumentFactory
    ) -> None:
        document_with_user_buyer = document_factory(
            buyer=Buyer.objects.get(employer=user_with_other_buyer.get_employer())
        )
        document_factory(buyer=buyer)
        response = docs_test_resource.request("list", user_with_other_buyer)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == document_with_user_buyer.id

    def test_list_filtered_access_contracts(
        self,
        user_with_other_buyer: User,
        buyer: Buyer,
        business_deal_factory: TypeBusinessDealFactory,
        contract_factory: TypeContractFactory,
        document_factory: TypeDocumentFactory,
        supplier_factory: TypeSupplierFactory,
    ) -> None:
        document_with_user_contract_buyer = document_factory(
            contract=contract_factory(
                business_deal=business_deal_factory(
                    buyer=Buyer.objects.get(employer=user_with_other_buyer.get_employer()),
                    supplier=supplier_factory(),
                ),
            ),
            buyer=None,
            supplier=None,
            product=None,
        )
        document_with_user_contract_supplier = document_factory(
            contract=contract_factory(
                business_deal=business_deal_factory(
                    buyer=buyer,
                    supplier=supplier_factory(employer=user_with_other_buyer.get_employer()),
                ),
            ),
            buyer=None,
            supplier=None,
            product=None,
        )
        document_factory()

        document_factory(buyer=buyer)
        response = docs_test_resource.request("list", user_with_other_buyer)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert response.data["results"][0]["id"] == document_with_user_contract_buyer.id
        assert response.data["results"][1]["id"] == document_with_user_contract_supplier.id

    def test_list_filtered_access_products(
        self,
        user_with_other_buyer: User,
        product_factory: TypeProductFactory,
        document_factory: TypeDocumentFactory,
        supplier_factory: TypeSupplierFactory,
    ) -> None:
        document_factory()
        user_document = document_factory(
            product=product_factory(supplier=supplier_factory(employer=user_with_other_buyer.get_employer()))
        )
        response = docs_test_resource.request("list", user_with_other_buyer)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == user_document.id

    def test_list_filtered_access_suppliers(
        self,
        user_with_other_buyer: User,
        supplier_factory: TypeSupplierFactory,
        document_factory: TypeDocumentFactory,
    ) -> None:
        document_factory()
        user_document = document_factory(
            supplier=supplier_factory(employer=user_with_other_buyer.get_employer()),
            buyer=None,
            contract=None,
            product=None,
        )
        response = docs_test_resource.request("list", user_with_other_buyer)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == user_document.id

    def test_list_filter_buyer(
        self, user: User, document_factory: TypeDocumentFactory, buyer_factory: TypeBuyerFactory
    ) -> None:
        buyer = buyer_factory(short_code="buy1")
        doc1 = document_factory(buyer=buyer)
        document_factory(buyer=buyer_factory(short_code="buy2"))
        doc3 = document_factory(buyer=buyer)
        response = docs_test_resource.request("list", user, data={"buyerId": buyer.id})
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert response.data["results"][0]["id"] == doc1.id
        assert response.data["results"][1]["id"] == doc3.id

    def test_list_filter_contract(
        self, user: User, contract_factory: TypeContractFactory, document_factory: TypeDocumentFactory
    ) -> None:
        contract = contract_factory()
        doc1 = document_factory(contract=contract)
        document_factory()
        doc3 = document_factory(contract=contract)
        response = docs_test_resource.request("list", user, data={"contractId": contract.id})
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert response.data["results"][0]["id"] == doc1.id
        assert response.data["results"][1]["id"] == doc3.id

    def test_list_filter_product(
        self, user: User, product_factory: TypeProductFactory, document_factory: TypeDocumentFactory
    ) -> None:
        product = product_factory()
        doc1 = document_factory(product=product)
        document_factory()
        doc3 = document_factory(product=product)
        response = docs_test_resource.request("list", user, data={"productId": product.id})
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert response.data["results"][0]["id"] == doc1.id
        assert response.data["results"][1]["id"] == doc3.id

    def test_list_filter_supplier(
        self, user, supplier_factory: TypeSupplierFactory, document_factory: TypeDocumentFactory
    ) -> None:
        supplier = supplier_factory()
        doc1 = document_factory(supplier=supplier)
        document_factory()
        doc3 = document_factory(supplier=supplier)
        response = docs_test_resource.request("list", user, data={"supplierId": supplier.id})
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert response.data["results"][0]["id"] == doc1.id
        assert response.data["results"][1]["id"] == doc3.id


@pytest.mark.django_db
class TestGetDocument:
    def test_get_document(self, user: User, document: Document) -> None:
        response = docs_test_resource.request("retrieve", user, pk=document.id)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == document.id

    def test_get_document_no_auth(self, document: Document) -> None:
        response = docs_test_resource.request("retrieve", None, pk=document.id)
        print(response.data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_document_bad_user_auth(self, user_with_other_buyer: User, document: Document) -> None:
        response = docs_test_resource.request("retrieve", user_with_other_buyer, pk=document.id)
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUploadDocument:
    def test_no_linked_fk_entities(self, user: User, document_type_factory: TypeDocumentTypeFactory) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        file = create_test_file()
        data = {
            "file": file,
            "name": file.name,
            "typeId": document_type_factory(name="text").id,
            "notes": "Fake file",
        }
        response: Response = docs_test_resource.request("create", user, data, content_type=None)
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["non_field_errors"][0] == ErrorDetail(
            string="Must supply buyer, contract, product, or supplier in request.", code="required"
        )

    def test_upload_document_buyer(
        self,
        user: User,
        buyer: Buyer,
        document_type_factory: TypeDocumentTypeFactory,
    ) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        file = create_test_file()
        data = {
            "file": file,
            "name": file.name,
            "buyerId": buyer.id,
            "typeId": document_type_factory(name="txt").id,
            "notes": "Fake file",
        }
        response: Response = docs_test_resource.request("create", user, data, content_type=None)
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["file"].startswith("http")

    def test_upload_document_contract(
        self,
        user: User,
        contract: Contract,
        document_type_factory: TypeDocumentTypeFactory,
    ) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        file = create_test_file()
        data = {
            "file": file,
            "name": file.name,
            "contractId": contract.id,
            "typeId": document_type_factory(name="txt").id,
            "notes": "Fake file",
        }
        response: Response = docs_test_resource.request("create", user, data, content_type=None)
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["file"].startswith("http")

    def test_upload_document_product(
        self,
        user: User,
        product: Product,
        document_type_factory: TypeDocumentTypeFactory,
    ) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        file = create_test_file()
        data = {
            "file": file,
            "name": file.name,
            "productId": product.id,
            "typeId": document_type_factory(name="txt").id,
            "notes": "Fake file",
        }
        response: Response = docs_test_resource.request("create", user, data, content_type=None)
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["file"].startswith("http")

    def test_upload_document_supplier(
        self,
        user: User,
        supplier: Supplier,
        document_type_factory: TypeDocumentTypeFactory,
    ) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        file = create_test_file()
        data = {
            "file": file,
            "name": file.name,
            "supplierId": supplier.id,
            "typeId": document_type_factory(name="txt").id,
        }
        response: Response = docs_test_resource.request("create", user, data, content_type=None)
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["file"].startswith("http")

    @pytest.mark.parametrize("key", ["buyerId", "contractId", "productId", "supplierId"])
    def test_upload_related_object_does_not_exist(
        self,
        user: User,
        document_type_factory: TypeDocumentTypeFactory,
        key: str,
    ) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        file = create_test_file()
        data = {
            "file": file,
            "name": file.name,
            key: 0,
            "typeId": document_type_factory(name="txt").id,
        }
        response: Response = docs_test_resource.request("create", user, data, content_type=None)
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_prevent_upload_unauth_related_buyer(
        self, user_with_other_buyer: User, buyer: Buyer, document_type_factory: TypeDocumentTypeFactory
    ) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        file = create_test_file()
        data = {
            "file": file,
            "name": file.name,
            "buyerId": buyer.id,
            "typeId": document_type_factory(name="txt").id,
            "notes": "Fake file",
        }
        response: Response = docs_test_resource.request("create", user_with_other_buyer, data, content_type=None)
        print(response.data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_prevent_upload_unauth_related_contract(
        self, user_with_other_buyer: User, contract: Contract, document_type_factory: TypeDocumentTypeFactory
    ) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        file = create_test_file()
        data = {
            "file": file,
            "name": file.name,
            "contractId": contract.id,
            "typeId": document_type_factory(name="txt").id,
            "notes": "Fake file",
        }
        response: Response = docs_test_resource.request("create", user_with_other_buyer, data, content_type=None)
        print(response.data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_prevent_upload_unauth_related_product(
        self, user_with_other_buyer: User, product: Product, document_type_factory: TypeDocumentTypeFactory
    ) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        file = create_test_file()
        data = {
            "file": file,
            "name": file.name,
            "productId": product.id,
            "typeId": document_type_factory(name="txt").id,
            "notes": "Fake file",
        }
        response: Response = docs_test_resource.request("create", user_with_other_buyer, data, content_type=None)
        print(response.data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_prevent_upload_unauth_related_supplier(
        self, user_with_other_buyer: User, supplier: Supplier, document_type_factory: TypeDocumentTypeFactory
    ) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        file = create_test_file()
        data = {
            "file": file,
            "name": file.name,
            "supplierId": supplier.id,
            "typeId": document_type_factory(name="txt").id,
            "notes": "Fake file",
        }
        response: Response = docs_test_resource.request("create", user_with_other_buyer, data, content_type=None)
        print(response.data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_prevent_upload_invalid_file_extension(self, user: User, buyer: Buyer, document_type: DocumentType) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        file = create_test_file(file_name="file.invalid")
        data = {
            "file": file,
            "name": file.name,
            "buyerId": buyer.id,
            "typeId": document_type.id,
            "notes": "Fake file",
        }
        response: Response = docs_test_resource.request("create", user, data, content_type=None)
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["name"][0] == ErrorDetail(
            "Filename extension does not match any valid file type (image, pdf, or office file).", code="invalid"
        )

    def test_prevent_upload_invalid_file_extension_from_file(
        self, user: User, buyer: Buyer, document_type_factory: TypeDocumentTypeFactory
    ) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        file = create_test_file(file_name="file.txt")
        data = {
            "file": file,
            "name": "file.pdf",
            "buyerId": buyer.id,
            "typeId": document_type_factory(name="txt").id,
            "notes": "Fake file",
        }
        response: Response = docs_test_resource.request("create", user, data, content_type=None)
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["file"][0] == ErrorDetail(
            "Filename extension does not match any valid file type (image, pdf, or office file).", code="invalid"
        )


@pytest.mark.django_db
class TestPatchDocumentMetadata:
    @pytest.mark.parametrize(
        ["key", "value"],
        [
            ("name", "file2.pdf"),
            ("notes", "New notes from patch"),
            ("date", "2021-03-08"),
            ("typeId", 1),
        ],
    )
    def test_update_fields(self, user: User, key: str, value: Any, document: Document) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        document.name = "file.pdf"
        document.save()

        response = docs_test_resource.request("partial_update", user, json.dumps({key: value}), pk=document.pk)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        if key == "typeId":
            assert response.data["type"]["id"] == value
        else:
            assert response.data[key] == value

    def test_invalid_filename_update(self, user: User, document: Document) -> None:
        AllowedDocumentFileExtension.objects.get_or_create(name="pdf")
        document.name = "file.png"
        document.save()

        response = docs_test_resource.request("partial_update", user, json.dumps({"name": "file.pdf"}), pk=document.pk)
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_not_allowed_to_update(self, user_with_other_buyer: User, document: Document) -> None:
        response = docs_test_resource.request("partial_update", user_with_other_buyer, "{}", pk=document.pk)
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDeleteDocument:
    def test_delete_document(self, user: User, document: Document) -> None:
        response = docs_test_resource.request("destroy", user, pk=document.pk)
        print(response.data)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_not_allowed_to_delete(self, user_with_other_buyer: User, document: Document) -> None:
        response = docs_test_resource.request("destroy", user_with_other_buyer, pk=document.pk)
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
