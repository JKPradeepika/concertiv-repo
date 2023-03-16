from django_filters import rest_framework as filters

from api.models.EmployerGeography import EmployerGeography


class EmployerGeographyFilterSet(filters.FilterSet):  # type: ignore
    buyerId = filters.NumberFilter(field_name="employer__buyer__id")

    class Meta:
        model = EmployerGeography
        fields = ["buyerId"]
