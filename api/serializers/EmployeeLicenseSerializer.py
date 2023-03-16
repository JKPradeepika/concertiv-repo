from typing import Any, Dict

from django.db import transaction
from rest_framework import serializers

from api.constants import LICENSES_PERIODS_STATUSES
from api.models.Employee import Employee
from api.models.Subscription import Subscription
from api.models.EmployeeLicense import EmployeeLicense
from api.serializers.EmployeeSerializer import EmployeeSerializer
from api.serializers.SubscriptionSerializer import SubscriptionSerializer
from api.helpers import ConstantChoiceField


class EmployeeLicenseSerializer(serializers.HyperlinkedModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employeeId = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), allow_empty=False, write_only=True)
    subscription = SubscriptionSerializer(read_only=True)
    subscriptionId = serializers.PrimaryKeyRelatedField(
        queryset=Subscription.objects.all(), allow_empty=False, write_only=True
    )
    startDate = serializers.DateField(source="start_date", allow_null=True)
    endDate = serializers.DateField(source="end_date", allow_null=True)
    status = ConstantChoiceField(LICENSES_PERIODS_STATUSES, read_only=True)

    class Meta:
        model = EmployeeLicense
        fields = [
            "id",
            "employee",
            "employeeId",
            "subscription",
            "subscriptionId",
            "startDate",
            "endDate",
            "status",
        ]

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> EmployeeLicense:
        employee = validated_data.pop("employeeId")
        validated_data["employee"] = employee
        subscription = validated_data.pop("subscriptionId")
        validated_data["subscription"] = subscription
        employee_license = EmployeeLicense.objects.create(**validated_data)

        return employee_license

    @transaction.atomic
    def update(self, instance: EmployeeLicense, validated_data: Dict[str, Any]) -> EmployeeLicense:
        employee = validated_data.pop("employeeId")
        validated_data["employee"] = employee
        subscription = validated_data.pop("subscriptionId")
        validated_data["subscription"] = subscription

        # Update direct fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
