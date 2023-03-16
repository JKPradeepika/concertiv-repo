from django_filters import rest_framework as filters

from api.models.ProductType import ProductType


class ProductTypeFilterSet(filters.FilterSet):  # type: ignore
    domainId = filters.NumberFilter(field_name="domain")

    class Meta:
        model = ProductType
        fields = ["domainId"]
