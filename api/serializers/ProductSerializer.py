from collections import OrderedDict
from django.db import transaction
from rest_framework import serializers
from typing import Any, Dict, List

from api.constants import DOMAINS, PRODUCT_STATUSES
from api.models.ProductType import ProductType
from api.models.Geography import Geography
from api.models.AgreementType import AgreementType
from api.models.Industry import Industry
from api.models.Product import Product
from api.models.Supplier import Supplier
from api.serializers.AgreementTypeSerializer import AgreementTypeSerializer
from api.serializers.ContactSerializer import ContactSerializer
from api.serializers.GeographySerializer import GeographySerializer
from api.serializers.IndustrySerializer import IndustrySerializer
from api.serializers.ProductTypeSerializer import ProductTypeSerializer
from api.translations import translations
from api.helpers import ConstantChoiceField


class ProductSupplierSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source="employer.name")

    class Meta:
        model = Supplier
        fields = ["id", "name"]


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    activeSubscriptionsCount = serializers.IntegerField(source="active_subscriptions_count", read_only=True)
    contacts = ContactSerializer(many=True, read_only=True)
    status = ConstantChoiceField(PRODUCT_STATUSES)
    domain = ConstantChoiceField(DOMAINS)
    supplier = ProductSupplierSerializer(read_only=True)
    supplierId = serializers.PrimaryKeyRelatedField(source="supplier", queryset=Supplier.objects.all(), write_only=True)
    industries = IndustrySerializer(many=True, read_only=True)
    industryIds = serializers.PrimaryKeyRelatedField(
        source="industries", queryset=Industry.objects.all(), write_only=True, required=True, many=True
    )
    types = ProductTypeSerializer(many=True, read_only=True)
    typeIds = serializers.PrimaryKeyRelatedField(
        source="types", queryset=ProductType.objects.all(), write_only=True, required=True, many=True
    )
    geographies = GeographySerializer(many=True, read_only=True)
    geographyIds = serializers.PrimaryKeyRelatedField(
        source="geographies", queryset=Geography.objects.all(), write_only=True, required=True, many=True
    )
    agreementType = AgreementTypeSerializer(source="agreement_type", read_only=True)
    agreementTypeId = serializers.PrimaryKeyRelatedField(
        source="agreement_type", queryset=AgreementType.objects.all(), write_only=True, required=False, allow_null=True
    )
    startDate = serializers.DateField(source="start_date", required=False, allow_null=True)
    endDate = serializers.DateField(source="end_date", required=False, allow_null=True)
    url = serializers.URLField(
        allow_blank=True,
        error_messages={"invalid": translations["Errors"]["InvalidUrl"]},
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "activeSubscriptionsCount",
            "contacts",
            "description",
            "domain",
            "status",
            "supplier",
            "supplierId",
            "industries",
            "industryIds",
            "types",
            "typeIds",
            "geographies",
            "geographyIds",
            "agreementType",
            "agreementTypeId",
            "startDate",
            "endDate",
            "url",
        ]

    @transaction.atomic
    def create(self, validated_data: OrderedDict[str, Any]) -> Product:
        # A list of types, industries and geographies objects
        product_types: List[ProductType] = validated_data.pop("types")
        product_industries: List[Industry] = validated_data.pop("industries", [])
        product_geographies: List[Geography] = validated_data.pop("geographies", [])
        product = Product.objects.create(**validated_data)
        for product_type in product_types:
            product.types.add(product_type)
        for product_industry in product_industries:
            product.industries.add(product_industry)
        for product_geography in product_geographies:
            product.geographies.add(product_geography)
        return product

    def update(self, instance: Product, validated_data: Dict[str, Any]) -> Product:
        # should not be able to update domain for a product after product creation
        validated_data.pop("domain", None)

        # A list of full types and industries objects
        product_types: List[ProductType] = validated_data.pop("types", [])
        product_industries: List[Industry] = validated_data.pop("industries", [])
        product_geographies: List[Industry] = validated_data.pop("geographies", [])
        # https://docs.djangoproject.com/en/4.1/ref/models/relations/#django.db.models.fields.related.RelatedManager.clear
        # removes objects from the related obj set, this doesn’t delete the related objects, it just disassociates them
        instance.types.clear()
        instance.industries.clear()
        instance.geographies.clear()
        # associate again types and industries
        for product_type in product_types:
            instance.types.add(product_type)
        for product_industry in product_industries:
            instance.industries.add(product_industry)
        for product_geography in product_geographies:
            instance.geographies.add(product_geography)

        # Update direct fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class SimpleProductSerializer(serializers.HyperlinkedModelSerializer):
    domain = ConstantChoiceField(choices=DOMAINS)

    class Meta:
        model = Product
        fields = ["id", "name", "domain"]
