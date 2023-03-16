from typing import Any, Dict, List

from django.db import transaction
from rest_framework import serializers

from api.models.Address import Address
from api.models.Employer import Employer
from api.models.Industry import Industry
from api.serializers.AddressSerializer import AddressSerializer
from api.serializers.IndustrySerializer import IndustrySerializer


class EmployerSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField()
    addresses = AddressSerializer(many=True, required=False)
    industries = IndustrySerializer(many=True)

    class Meta:
        model = Employer
        fields = [
            "id",
            "name",
            "addresses",
            "industries",
        ]

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> Employer:
        addresses_data = validated_data.pop("addresses", [])
        industries: List[Industry] = validated_data.pop("industries", [])
        employer = Employer.objects.create(**validated_data)

        for industry in industries:
            employer.industries.add(industry)

        for address_data in addresses_data:
            address, _ = Address.objects.get_or_create(**address_data)
            employer.addresses.add(address.id)
        employer.save()

        return employer

    @transaction.atomic
    def update(self, instance: Employer, validated_data: Dict[str, Any]) -> Employer:
        industries: List[Industry] = validated_data.pop("industries", [])
        instance.industries.clear()
        for industry in industries:
            instance.industries.add(industry)

        # Update direct fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
