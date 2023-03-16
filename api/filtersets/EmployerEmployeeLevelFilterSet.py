from django_filters import rest_framework as filters

from api.models.EmployerEmployeeLevel import EmployerEmployeeLevel


class EmployerEmployeeLevelFilterSet(filters.FilterSet):  # type: ignore
    buyerId = filters.NumberFilter(field_name="employer__buyer__id")

    class Meta:
        model = EmployerEmployeeLevel
        fields = ["buyerId"]
