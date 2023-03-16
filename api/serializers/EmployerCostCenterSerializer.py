from typing import Any, Dict

from django.db import transaction
from rest_framework import serializers

from api.models.Employer import Employer
from api.models.EmployerCostCenter import EmployerCostCenter
from api.serializers.EmployerSerializer import EmployerSerializer


class EmployerCostCenterSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField()
    employer = EmployerSerializer(read_only=True)
    employerId = serializers.PrimaryKeyRelatedField(queryset=Employer.objects.all(), allow_empty=False, write_only=True)

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> EmployerCostCenter:
        employer = validated_data.pop("employerId")
        validated_data["employer"] = employer

        return EmployerCostCenter.objects.create(**validated_data)

    class Meta:
        model = EmployerCostCenter
        fields = ["id", "name", "employer", "employerId"]
