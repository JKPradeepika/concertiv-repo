from django.db.models import QuerySet
from rest_framework import viewsets
from api.filtersets import SupplierFilterSet

from api.models.Supplier import Supplier
from api.policies import CustomDjangoModelPermissions, SupplierAccessPolicy
from api.serializers.SupplierSerializer import SupplierSerializer
from api.viewsets.ViewSetHelpers import PageSetPagination, sort_and_filter_queryset

# unfilterable: ndasigned (No/Yes instead of True/False), Domains, Industries, Primary Contact
column_name_mappings = {
    "name": "employer__name",
    "description": "description",
    "url": "url",
    "productscount": "products_count",
    "isndasigned": "is_nda_signed",
    "domains": "products__domain",
}


class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, SupplierAccessPolicy]
    pagination_class = PageSetPagination
    filterset_class = SupplierFilterSet
    serializer_class = SupplierSerializer

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[Supplier]:
        queryset = Supplier.objects.order_by("id").prefetch_related(
            "employer",
            "employer__persons__contact",
            "employer__industries",
        )
        queryset = sort_and_filter_queryset(
            initial_queryset=queryset, column_name_mappings=column_name_mappings, query_params=self.request.query_params
        )
        return SupplierAccessPolicy.scope_queryset(self.request, queryset)
