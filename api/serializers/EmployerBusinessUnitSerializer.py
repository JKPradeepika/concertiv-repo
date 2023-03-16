from typing import Any, Dict

from django.db import transaction
from rest_framework import serializers

from api.models.Employer import Employer
from api.models.EmployerBusinessUnit import EmployerBusinessUnit
from api.serializers.EmployerSerializer import EmployerSerializer


class EmployerBusinessUnitSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField()
    employer = EmployerSerializer(read_only=True)
    employerId = serializers.PrimaryKeyRelatedField(queryset=Employer.objects.all(), allow_empty=False, write_only=True)

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> EmployerBusinessUnit:
        employer = validated_data.pop("employerId")
        validated_data["employer"] = employer

        return EmployerBusinessUnit.objects.create(**validated_data)

    class Meta:
        model = EmployerBusinessUnit
        fields = ["id", "name", "employer", "employerId"]
