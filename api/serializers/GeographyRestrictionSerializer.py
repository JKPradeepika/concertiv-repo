from rest_framework import serializers
from api.models.EmployerGeography import EmployerGeography

from api.models.GeographyRestriction import GeographyRestriction
from api.models.Subscription import Subscription


class GeographyRestrictionSerializer(serializers.HyperlinkedModelSerializer):
    subscriptionId = serializers.PrimaryKeyRelatedField(
        source="subscription", queryset=Subscription.objects.all(), required=False, allow_null=True
    )
    employerGeographyId = serializers.PrimaryKeyRelatedField(
        source="employer_geography",
        queryset=EmployerGeography.objects.all(),
        required=True,
    )
    name = serializers.CharField(source="employer_geography.name")

    class Meta:
        model = GeographyRestriction
        fields = ["id", "employerGeographyId", "subscriptionId", "name"]
