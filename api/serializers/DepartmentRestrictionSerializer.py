from rest_framework import serializers
from api.models.EmployerDepartment import EmployerDepartment

from api.models.DepartmentRestriction import DepartmentRestriction
from api.models.Subscription import Subscription


class DepartmentRestrictionSerializer(serializers.HyperlinkedModelSerializer):
    subscriptionId = serializers.PrimaryKeyRelatedField(
        source="subscription", queryset=Subscription.objects.all(), required=False, allow_null=True
    )
    employerDepartmentId = serializers.PrimaryKeyRelatedField(
        source="employer_department",
        queryset=EmployerDepartment.objects.all(),
        required=True,
    )
    name = serializers.CharField(source="employer_department.name")

    class Meta:
        model = DepartmentRestriction
        fields = ["id", "employerDepartmentId", "subscriptionId", "name"]
