from django.db.models import QuerySet
from rest_framework import viewsets

from api.filtersets import EmployeeLicenseFilterSet
from api.models.EmployeeLicense import EmployeeLicense, EmployeeLicenseManager
from api.models.Subscription import SubscriptionManager
from api.policies import CustomDjangoModelPermissions, EmployeeLicenseAccessPolicy
from api.serializers.EmployeeLicenseSerializer import EmployeeLicenseSerializer
from api.viewsets.ViewSetHelpers import PageSetPagination, sort_and_filter_queryset

SUBSCRIPTION_PREFIX = "subscription__"
CONTRACT_PREFIX = SUBSCRIPTION_PREFIX + "contract__"

column_name_mappings = {
    "firstname": "employee__person__first_name",
    "lastname": "employee__person__last_name",
    "productname": SUBSCRIPTION_PREFIX + "product__name",
    "licensestatus": "status",
    "licensestartdate": "start_date",
    "licenseenddate": "end_date",
    "contractstatus": CONTRACT_PREFIX + "status",
    "subscriptionname": SUBSCRIPTION_PREFIX + "name",
    "billingfrequency": SUBSCRIPTION_PREFIX + "billing_frequency",
    "subscriptionusercount": SUBSCRIPTION_PREFIX + "employee_license_count",
}


class EmployeeLicenseViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, EmployeeLicenseAccessPolicy]
    filterset_class = EmployeeLicenseFilterSet
    pagination_class = PageSetPagination

    def get_queryset(self) -> QuerySet[EmployeeLicense]:
        queryset = EmployeeLicense.objects.order_by("id")
        queryset = (
            queryset.annotate(**EmployeeLicenseManager.get_status_annotation_kwargs())
            .annotate(**SubscriptionManager.get_annotation_kwargs(join_prefix=SUBSCRIPTION_PREFIX))
            .distinct()
        )
        queryset = sort_and_filter_queryset(
            initial_queryset=queryset, column_name_mappings=column_name_mappings, query_params=self.request.query_params
        )
        return EmployeeLicenseAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = EmployeeLicenseSerializer
