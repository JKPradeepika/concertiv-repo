from rest_framework import serializers
from api.models.EmployerCoverageGroup import EmployerCoverageGroup

from api.models.CoverageGroupRestriction import CoverageGroupRestriction
from api.models.Subscription import Subscription


class CoverageGroupRestrictionSerializer(serializers.HyperlinkedModelSerializer):
    subscriptionId = serializers.PrimaryKeyRelatedField(
        source="subscription", queryset=Subscription.objects.all(), required=False, allow_null=True
    )
    employerCoverageGroupId = serializers.PrimaryKeyRelatedField(
        source="employer_coverage_group",
        queryset=EmployerCoverageGroup.objects.all(),
        required=True,
    )
    name = serializers.CharField(source="employer_coverage_group.name")

    class Meta:
        model = CoverageGroupRestriction
        fields = [
            "id",
            "employerCoverageGroupId",
            "name",
            "subscriptionId",
        ]
