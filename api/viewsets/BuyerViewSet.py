from django.db.models import QuerySet
from rest_framework import viewsets

from api.models.Buyer import Buyer
from api.policies import BuyerAccessPolicy, CustomDjangoModelPermissions
from api.serializers.BuyerSerializer import BuyerSerializer
from api.viewsets.ViewSetHelpers import PageSetPagination, sort_and_filter_queryset

column_name_mappings = {
    "name": "employer__name",
    "shortname": "short_name",
    "shortcode": "short_code",
    "accountstatus": "account_status",
    "activesubscriptionscount": "active_subscriptions_count",
    "firstjoinedat": "first_joined_at",
}


class BuyerViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, BuyerAccessPolicy]
    pagination_class = PageSetPagination

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[Buyer]:
        queryset = Buyer.objects.order_by("id").prefetch_related(
            "employer",
            "employer__addresses",
            "employer__persons__contact",
            "employer__industries",
        )

        queryset = sort_and_filter_queryset(
            initial_queryset=queryset, column_name_mappings=column_name_mappings, query_params=self.request.query_params
        )

        return BuyerAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = BuyerSerializer
