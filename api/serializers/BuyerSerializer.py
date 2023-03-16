from typing import Any, Dict, List

from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.constants import BUYER_STATUSES
from api.models.Geography import Geography
from api.models.BusinessType import BusinessType
from api.models.Buyer import Buyer
from api.models.Contact import Contact
from api.models.Industry import Industry
from api.serializers.BusinessTypeSerializer import BusinessTypeSerializer
from api.serializers.AddressSerializer import AddressSerializer
from api.serializers.ContactSerializer import ContactSerializer
from api.serializers.EmployerSerializer import EmployerSerializer
from api.serializers.GeographySerializer import GeographySerializer
from api.serializers.IndustrySerializer import IndustrySerializer
from api.helpers import ConstantChoiceField


class BuyerSerializer(serializers.HyperlinkedModelSerializer):

    name = serializers.CharField(source="employer.name")
    shortName = serializers.CharField(source="short_name")
    shortCode = serializers.CharField(
        source="short_code",
        max_length=Buyer._meta.get_field("short_code").max_length,
        validators=[UniqueValidator(queryset=Buyer.objects.all(), message="This client code already exists.")],
    )
    accountStatus = ConstantChoiceField(BUYER_STATUSES, source="account_status")
    savingsReportFrequencyInMonths = serializers.IntegerField(
        source="savings_report_frequency_in_months", required=False, allow_null=True
    )
    firstJoinedAt = serializers.DateField(source="first_joined_at")
    terminationDate = serializers.DateField(source="termination_date", required=False)
    activeSubscriptionsCount = serializers.IntegerField(source="active_subscriptions_count", read_only=True)
    addresses = AddressSerializer(source="employer.addresses", many=True, required=False)
    contacts = serializers.SerializerMethodField()
    industries = IndustrySerializer(many=True, read_only=True)
    industryIds = serializers.PrimaryKeyRelatedField(
        source="industries", queryset=Industry.objects.all(), write_only=True, required=True, many=True
    )
    geographies = GeographySerializer(many=True, read_only=True)
    geographyIds = serializers.PrimaryKeyRelatedField(
        source="geographies", queryset=Geography.objects.all(), write_only=True, required=True, many=True
    )
    businessType = BusinessTypeSerializer(source="business_type", read_only=True)
    businessTypeId = serializers.PrimaryKeyRelatedField(
        source="business_type", queryset=BusinessType.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Buyer
        fields = [
            "id",
            "name",
            "shortName",
            "shortCode",
            "accountStatus",
            "savingsReportFrequencyInMonths",
            "firstJoinedAt",
            "terminationDate",
            "activeSubscriptionsCount",
            "addresses",
            "contacts",
            "industries",
            "industryIds",
            "geographies",
            "geographyIds",
            "businessType",
            "businessTypeId",
        ]

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> Buyer:
        employer = EmployerSerializer().create(validated_data["employer"])
        validated_data["employer"] = employer
        # A list of types, industries and geographies objects (for MTM relationship)
        buyer_industries: List[Industry] = validated_data.pop("industries", [])
        buyer_geographies: List[Geography] = validated_data.pop("geographies", [])
        # create obj
        buyer = Buyer.objects.create(**validated_data)
        # associate MTM objects to Buyer
        for buyer_industry in buyer_industries:
            buyer.industries.add(buyer_industry)
            # this was in employer serializer before this decision to also associate industries to buyer
            employer.industries.add(buyer_industry)
        for buyer_geography in buyer_geographies:
            buyer.geographies.add(buyer_geography)
        return buyer

    @transaction.atomic
    def update(self, instance: Buyer, validated_data: Dict[str, Any]) -> Buyer:
        # should not be able to update domain for a buyer after buyer creation
        validated_data.pop("domain", None)

        if "employer" in validated_data:
            EmployerSerializer().update(instance.employer, validated_data["employer"])
            validated_data.pop("employer")

        # A list of industries and geographies MTM (for MTM relationship, disassociate and associate it again)
        buyer_industries: List[Industry] = validated_data.pop("industries", [])
        buyer_geographies: List[Industry] = validated_data.pop("geographies", [])
        instance.industries.clear()
        instance.geographies.clear()
        for buyer_industry in buyer_industries:
            instance.industries.add(buyer_industry)
        for buyer_geography in buyer_geographies:
            instance.geographies.add(buyer_geography)

        # Update direct fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    @staticmethod
    def get_contacts(obj: Buyer) -> Dict[str, Any]:
        return ContactSerializer(instance=Contact.objects.filter(person__employer=obj.employer), many=True).data


class SimpleBuyerSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source="employer.name")

    class Meta:
        model = Buyer
        fields = [
            "id",
            "name",
        ]
