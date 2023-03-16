from django_filters import rest_framework as filters

from api.models.EmployerDepartment import EmployerDepartment


class EmployerDepartmentFilterSet(filters.FilterSet):  # type: ignore
    buyerId = filters.NumberFilter(field_name="employer__buyer__id")

    class Meta:
        model = EmployerDepartment
        fields = ["buyerId"]
