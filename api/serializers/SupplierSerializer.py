from typing import Any, Dict

from django.db import transaction
from rest_framework import serializers

from api.constants import DOMAINS, SUPPLIER_TYPES
from api.helpers import ConstantChoiceField
from api.models.Supplier import Supplier
from api.serializers.AddressSerializer import AddressSerializer
from api.serializers.ContactSerializer import ContactSerializer
from api.serializers.EmployerSerializer import EmployerSerializer
from api.translations import translations


class SupplierSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source="employer.name")
    description = serializers.CharField(allow_blank=True, required=False)
    isNdaSigned = serializers.BooleanField(source="is_nda_signed")
    productsCount = serializers.IntegerField(source="products_count", read_only=True)
    contacts = ContactSerializer(many=True, read_only=True)
    addresses = AddressSerializer(source="employer.addresses", many=True, read_only=True)
    type = ConstantChoiceField(choices=SUPPLIER_TYPES, read_only=True)
    typeId = ConstantChoiceField(choices=SUPPLIER_TYPES, source="type", write_only=True)
    url = serializers.URLField(
        allow_blank=True,
        error_messages={"invalid": translations["Errors"]["InvalidUrl"]},
        required=False,
    )
    # only to be used in the UI to show the domains related with the supplier based on its related products
    domains = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "description",
            "isNdaSigned",
            "url",
            "productsCount",
            "contacts",
            "addresses",
            "type",
            "typeId",
            "domains",
        ]

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> Supplier:
        employer = EmployerSerializer().create(validated_data["employer"])
        validated_data["employer"] = employer
        return Supplier.objects.create(**validated_data)

    @transaction.atomic
    def update(self, instance: Supplier, validated_data: Dict[str, Any]) -> Supplier:
        if "employer" in validated_data:
            EmployerSerializer().update(instance.employer, validated_data["employer"])
            validated_data.pop("employer")

        # Update direct fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    @staticmethod
    def get_domains(obj):
        return ", ".join([str(dict(DOMAINS)[x]) for x in obj.products.values_list("domain", flat=True).distinct()])


class SimpleSupplierSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source="employer.name")

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
        ]
