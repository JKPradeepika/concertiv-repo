from django_filters import rest_framework as filters

from api.models.EmployerBusinessUnit import EmployerBusinessUnit


class EmployerBusinessUnitFilterSet(filters.FilterSet):  # type: ignore
    buyerId = filters.NumberFilter(field_name="employer__buyer__id")

    class Meta:
        model = EmployerBusinessUnit
        fields = ["buyerId"]
