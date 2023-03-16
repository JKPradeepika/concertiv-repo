from django_filters import rest_framework as filters

from api.models.EmployeeLicense import EmployeeLicense


class EmployeeLicenseFilterSet(filters.FilterSet):  # type: ignore
    buyerId = filters.NumberFilter(field_name="employee__person__employer__buyer__id")
    contractId = filters.NumberFilter(field_name="subscription__contract__id")
    employeeId = filters.NumberFilter(field_name="employee__id")
    subscriptionId = filters.NumberFilter(field_name="subscription__id")

    class Meta:
        model = EmployeeLicense
        fields = ["buyerId", "contractId", "employeeId", "subscriptionId"]
