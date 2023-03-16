from typing import Any, Dict

from django.db import transaction
from rest_framework import serializers

from api.models.Employer import Employer
from api.models.EmployerDepartment import EmployerDepartment
from api.serializers.EmployerSerializer import EmployerSerializer


class EmployerDepartmentSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField()
    employer = EmployerSerializer(read_only=True)
    employerId = serializers.PrimaryKeyRelatedField(queryset=Employer.objects.all(), allow_empty=False, write_only=True)

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> EmployerDepartment:
        employer = validated_data.pop("employerId")
        validated_data["employer"] = employer

        return EmployerDepartment.objects.create(**validated_data)

    class Meta:
        model = EmployerDepartment
        fields = ["id", "name", "employer", "employerId"]
