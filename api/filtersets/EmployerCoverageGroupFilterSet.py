from django_filters import rest_framework as filters

from api.models.EmployerCoverageGroup import EmployerCoverageGroup


class EmployerCoverageGroupFilterSet(filters.FilterSet):  # type: ignore
    buyerId = filters.NumberFilter(field_name="employer__buyer__id")

    class Meta:
        model = EmployerCoverageGroup
        fields = ["buyerId"]
