from django.db.models import QuerySet
from rest_framework import viewsets

from api.filtersets.ContractFilterSet import ContractFilterSet
from api.models.Contract import Contract
from api.models.LicensePeriod import LicensePeriodManager
from api.models.Subscription import SubscriptionManager
from api.policies import ContractAccessPolicy, CustomDjangoModelPermissions
from api.serializers.ContractSerializer import ContractSerializer
from api.viewsets.ViewSetHelpers import PageSetPagination, sort_and_filter_queryset

LICENSES_PERIODS_PREFIX = "business_deal__contracts__subscriptions__licenses_periods__"

column_name_mappings = {
    "subscriptionname": "subscriptions__name",
    "supplier": "business_deal__supplier__employer__name",
    "licenseperiodstartdate": LICENSES_PERIODS_PREFIX + "start_date",
    "licenseperiodenddate": LICENSES_PERIODS_PREFIX + "end_date",
    "licenseperiodprice": LICENSES_PERIODS_PREFIX + "price",
    "licenseperiodstatus": LICENSES_PERIODS_PREFIX + "status",
    "status": "status",
    "autorenewaldeadline": "autorenewal_deadline",
    "product": "subscriptions__product__name",
    "licenseperiodtype": LICENSES_PERIODS_PREFIX + "type",
    "startdate": "start_date",
    "enddate": "end_date",
    "signeddate": "signed_date",
    "buyerentityname": "business_deal__buyer__employer__name",
    "licenseperiodmaxusers": LICENSES_PERIODS_PREFIX + "max_users",
    "licenseperiodmaxcredits": LICENSES_PERIODS_PREFIX + "max_credits",
    "licenseperiodpricecurrency": LICENSES_PERIODS_PREFIX + "price_currency",
    "doesautorenew": "subscriptions__does_autorenew",
    "taxrate": "subscriptions__tax_rate",
    "billingfrequency": "subscriptions__billing_frequency",
    "subscriptionismultiterm": "subscriptions__is_multiterm",
}


class ContractViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, ContractAccessPolicy]
    filterset_class = ContractFilterSet
    pagination_class = PageSetPagination

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[Contract]:
        queryset = Contract.objects.prefetch_related(
            "business_deal",
            "business_deal__buyer",
            "business_deal__supplier",
            "subscriptions",
            "subscriptions__product",
            "subscriptions__licenses_periods",
        )
        queryset = (
            queryset.annotate(**LicensePeriodManager.get_status_annotation_kwargs(join_prefix=LICENSES_PERIODS_PREFIX))
            .annotate(**SubscriptionManager.get_annotation_kwargs(join_prefix="subscriptions__"))
            .distinct()
        )
        queryset = sort_and_filter_queryset(
            initial_queryset=queryset, column_name_mappings=column_name_mappings, query_params=self.request.query_params
        )
        return ContractAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = ContractSerializer
