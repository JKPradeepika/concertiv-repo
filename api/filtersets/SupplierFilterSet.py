from django.db.models import QuerySet
from django_filters import rest_framework as filters
from api.models.Supplier import Supplier


class SupplierFilterSet(filters.FilterSet):  # type: ignore
    contains_products = filters.BooleanFilter(field_name="products_count", method="filter_contains_products")
    domainId = filters.NumberFilter(field_name="products__domain")
    typeId = filters.NumberFilter(field_name="type")

    def filter_contains_products(self, queryset: QuerySet[Supplier], name, value):
        if value:
            return queryset.filter(**{"products_count__gt": 0})
        return queryset.filter(**{"products_count": 0})

    class Meta:
        model = Supplier
        fields = ["contains_products", "domainId", "type"]
