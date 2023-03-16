from django.db.models import QuerySet
from rest_framework import viewsets

from api.models.LicensePeriod import LicensePeriod
from api.models.Subscription import SubscriptionManager
from api.policies import CustomDjangoModelPermissions
from api.serializers.LicensePeriodSerializer import LicensePeriodSerializer
from api.viewsets.ViewSetHelpers import PageSetPagination, sort_and_filter_queryset
from api.filtersets.LicensePeriodFilterSet import LicensePeriodFilterSet
from api.policies.LicensePeriodAccessPolicy import LicensePeriodAccessPolicy

SUBSCRIPTION_PREFIX = "subscription__"
CONTRACT_PREFIX = SUBSCRIPTION_PREFIX + "contract__"

column_name_mappings = {
    "subscriptionname": SUBSCRIPTION_PREFIX + "name",
    "supplier": CONTRACT_PREFIX + "business_deal__supplier__employer__name",
    "startdate": "start_date",
    "enddate": "end_date",
    "price": "price",
    "status": "status",
    "contractstatus": CONTRACT_PREFIX + "status",
    "autorenewaldeadline": CONTRACT_PREFIX + "autorenewal_deadline",
    "product": SUBSCRIPTION_PREFIX + "product__name",
    "type": "type",
    "contractstartdate": CONTRACT_PREFIX + "start_date",
    "contractenddate": CONTRACT_PREFIX + "end_date",
    "signeddate": CONTRACT_PREFIX + "signed_date",
    "buyerentityname": CONTRACT_PREFIX + "business_deal__buyer__employer__name",
    "billingfrequency": SUBSCRIPTION_PREFIX + "billing_frequency",
    "maxusers": "max_users",
    "maxcredits": "max_credits",
    "pricecurrency": "price_currency",
    "taxrate": SUBSCRIPTION_PREFIX + "tax_rate",
    "clientname": CONTRACT_PREFIX + "business_deal__buyer__employer__name",
    "subscriptionismultiterm": SUBSCRIPTION_PREFIX + "is_multiterm",
    "doesautorenew": SUBSCRIPTION_PREFIX + "does_autorenew",
}


class LicensePeriodViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomDjangoModelPermissions]
    pagination_class = PageSetPagination
    filterset_class = LicensePeriodFilterSet

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[LicensePeriod]:
        queryset = LicensePeriod.objects.annotate(
            **SubscriptionManager.get_annotation_kwargs(join_prefix=SUBSCRIPTION_PREFIX)
        ).order_by("id")
        queryset = sort_and_filter_queryset(
            initial_queryset=queryset, column_name_mappings=column_name_mappings, query_params=self.request.query_params
        )
        return LicensePeriodAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = LicensePeriodSerializer
