from django_filters import rest_framework as filters

from api.models.Employee import Employee


class EmployeeFilterSet(filters.FilterSet):  # type: ignore
    buyerId = filters.NumberFilter(field_name="person__employer__buyer__id")

    class Meta:
        model = Employee
        fields = ["buyerId"]
