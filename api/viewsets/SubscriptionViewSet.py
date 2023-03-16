from django.db.models import QuerySet
from rest_framework import viewsets

from api.filtersets.SubscriptionFilterSet import SubscriptionFilterSet
from api.models.Subscription import Subscription
from api.models.LicensePeriod import LicensePeriodManager
from api.policies import CustomDjangoModelPermissions
from api.policies.SubscriptionAccessPolicy import SubscriptionAccessPolicy
from api.serializers.SubscriptionSerializer import SubscriptionSerializer
from api.viewsets.ViewSetHelpers import PageSetPagination, sort_and_filter_queryset

LICENSES_PERIODS_PREFIX = "licenses_periods__"

column_name_mappings = {
    "startdate": "start_date",
    "enddate": "end_date",
    "product": "product__name",
    "supplier": "contract__business_deal__supplier__employer__name",
    "buyerentityname": "contract__business_deal__buyer__employer__name",
    "licenseperiodstartdate": LICENSES_PERIODS_PREFIX + "start_date",
    "licenseperiodenddate": LICENSES_PERIODS_PREFIX + "end_date",
    "licenseperiodprice": LICENSES_PERIODS_PREFIX + "price",
    "licenseperiodstatus": LICENSES_PERIODS_PREFIX + "status",
    "licenseperiodtype": LICENSES_PERIODS_PREFIX + "type",
    "licenseperiodmaxusers": LICENSES_PERIODS_PREFIX + "max_users",
    "licenseperiodmaxcredits": LICENSES_PERIODS_PREFIX + "max_credits",
    "licenseperiodpricecurrency": LICENSES_PERIODS_PREFIX + "price_currency",
    "billingfrequency": "billing_frequency",
    "taxrate": "tax_rate",
    "ismultiterm": "is_multiterm",
    "employeelicensecount": "employee_license_count",
    "doesautorenew": "does_autorenew",
}


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, SubscriptionAccessPolicy]
    filterset_class = SubscriptionFilterSet
    pagination_class = PageSetPagination

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[Subscription]:
        queryset = Subscription.objects.prefetch_related(
            "contract__business_deal",
            "contract__business_deal__buyer",
            "contract__business_deal__supplier",
            "product",
            "licenses_periods",
        )
        queryset = queryset.annotate(
            **LicensePeriodManager.get_status_annotation_kwargs(join_prefix=LICENSES_PERIODS_PREFIX)
        ).distinct()
        queryset = sort_and_filter_queryset(
            initial_queryset=queryset, column_name_mappings=column_name_mappings, query_params=self.request.query_params
        )
        return SubscriptionAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = SubscriptionSerializer
