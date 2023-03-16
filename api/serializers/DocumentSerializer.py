from typing import OrderedDict, Optional

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from api.constants import MAX_FILE_BYTES, MAX_FILE_SIZE_PRETTY_NAME
from api.models import AllowedDocumentFileExtension
from api.models import Buyer, Contract, Document, DocumentType, Product, Supplier
from api.serializers import BuyerSerializer
from api.serializers.ProductSerializer import ProductSerializer
from api.serializers.SupplierSerializer import SupplierSerializer
from api.serializers.SimpleContractSerializer import SimpleContractSerializer


ERR_MSG_SUPPLY_LINKED_ENTITY = _("Must supply buyer, contract, product, or supplier in request.")
ERR_MSG_INVALID_FILE_EXTENSION = _("Filename must include a valid file extension.")
ERR_MSG_FILE_EXT_MISMATCH = _("Filename extension does not match any valid file type (image, pdf, or office file).")
ERR_MSG_MAX_FILE_SIZE_EXCEEDED = _(f"This upload exceeds max upload size of {MAX_FILE_SIZE_PRETTY_NAME}.")


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ["id", "name"]


class DocumentMetadataSerializer(serializers.ModelSerializer):
    buyerId = serializers.PrimaryKeyRelatedField(
        source="buyer", queryset=Buyer.objects.all(), write_only=True, allow_null=True, required=False
    )
    buyer = BuyerSerializer(read_only=True)
    contractId = serializers.PrimaryKeyRelatedField(
        source="contract", queryset=Contract.objects.all(), write_only=True, allow_null=True, required=False
    )
    contract = SimpleContractSerializer(read_only=True)
    productId = serializers.PrimaryKeyRelatedField(
        source="product", queryset=Product.objects.all(), write_only=True, allow_null=True, required=False
    )
    product = ProductSerializer(read_only=True)
    supplierId = serializers.PrimaryKeyRelatedField(
        source="supplier", queryset=Supplier.objects.all(), write_only=True, allow_null=True, required=False
    )
    supplier = SupplierSerializer(read_only=True)
    typeId = serializers.PrimaryKeyRelatedField(source="type", queryset=DocumentType.objects.all(), write_only=True)
    type = DocumentTypeSerializer(read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    date = serializers.DateField(required=False)

    class Meta:
        model = Document
        fields = [
            "id",
            "name",
            "date",
            "notes",
            "buyerId",
            "contractId",
            "productId",
            "supplierId",
            "type",
            "typeId",
            "buyer",
            "contract",
            "product",
            "supplier",
            "updatedAt",
        ]

    def validate(self, data: OrderedDict):
        data = super().validate(data)

        update_instance = self.get_update_instance()
        if update_instance:
            return self._validate_update(update_instance, data)

        return self._validate_upload_metadata(data)

    def get_update_instance(self) -> Optional[Document]:
        return getattr(self.root, "instance", None)

    def _validate_update(self, document: Document, data: OrderedDict) -> None:
        if "name" in data:
            self._validate_file_extension(data["name"], "name", self._get_filename_extension(document.name))

        return data

    def _validate_upload_metadata(self, data: OrderedDict) -> None:
        if not any([data.get("buyer"), data.get("contract"), data.get("product"), data.get("supplier")]):
            raise serializers.ValidationError(
                {"non_field_errors": [serializers.ErrorDetail(string=ERR_MSG_SUPPLY_LINKED_ENTITY, code="required")]}
            )
        self._validate_file_extension(data.get("name", ""), field="name")
        return data

    @staticmethod
    def _get_filename_extension(filename: str) -> Optional[str]:
        filename_components = filename.rsplit(".", 1)
        if len(filename_components) < 2:
            return None
        return filename_components[1]

    def _validate_file_extension(
        self, filename: str, field: str = "name", match_file_ext: Optional[str] = None
    ) -> None:
        file_ext = self._get_filename_extension(filename)
        if not file_ext:
            raise serializers.ValidationError(
                {field: [serializers.ErrorDetail(string=ERR_MSG_INVALID_FILE_EXTENSION, code="invalid")]}
            )
        if not AllowedDocumentFileExtension.objects.filter(name__iexact=file_ext.lower()).exists():
            raise serializers.ValidationError(
                {field: [serializers.ErrorDetail(string=ERR_MSG_FILE_EXT_MISMATCH, code="invalid")]}
            )
        if match_file_ext and match_file_ext.lower() != file_ext.lower():
            raise serializers.ValidationError(
                {
                    field: [
                        serializers.ErrorDetail(string=_("Cannot update file to different extension."), code="invalid")
                    ]
                }
            )


class DocumentSerializer(DocumentMetadataSerializer):
    file = serializers.FileField()

    class Meta:
        model = Document
        fields = DocumentMetadataSerializer.Meta.fields + [
            "file",
        ]

    def validate(self, data: OrderedDict):
        data = super().validate(data)
        self._validate_file_extension(data["file"].name, field="file")
        if data["file"].size > MAX_FILE_BYTES:
            raise serializers.ValidationError(
                {"file": [serializers.ErrorDetail(string=ERR_MSG_MAX_FILE_SIZE_EXCEEDED, code="invalid")]}
            )
        data["file"].name = data["name"]
        return data
