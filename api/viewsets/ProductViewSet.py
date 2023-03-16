from django.db.models import QuerySet
from rest_framework import viewsets

from api.filtersets import ProductFilterSet
from api.models.Product import Product
from api.policies import CustomDjangoModelPermissions, ProductAccessPolicy
from api.serializers.ProductSerializer import ProductSerializer
from api.viewsets.ViewSetHelpers import PageSetPagination, sort_and_filter_queryset

# unfilertable: contacts, primarycontact
column_name_mappings = {
    "name": "name",
    "supplier": "supplier__employer__name",
    "status": "status",
    "domain": "domain",
    "activesubscriptionscount": "active_subscriptions_count",
    "firstjoinedat": "created_at",
    "industry": "industries__name",
}


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, ProductAccessPolicy]
    pagination_class = PageSetPagination
    filterset_class = ProductFilterSet

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[Product]:
        queryset = Product.objects.prefetch_related(
            "contacts", "supplier", "supplier__employer", "supplier__employer__industries", "types"
        )
        queryset = sort_and_filter_queryset(
            initial_queryset=queryset, column_name_mappings=column_name_mappings, query_params=self.request.query_params
        )
        return ProductAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = ProductSerializer
