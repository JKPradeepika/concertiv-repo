from django_filters import rest_framework as filters

from api.models.Product import Product


class ProductFilterSet(filters.FilterSet):  # type: ignore
    supplierId = filters.NumberFilter(field_name="supplier_id")
    domainId = filters.NumberFilter(field_name="domain")

    class Meta:
        model = Product
        fields = ["domainId", "supplierId"]
