from rest_framework import viewsets

from api.filtersets import ProductTypeFilterSet
from api.models.ProductType import ProductType
from api.serializers.ProductTypeSerializer import ProductTypeSerializer


class ProductTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductType.objects.order_by("id")
    serializer_class = ProductTypeSerializer
    filterset_class = ProductTypeFilterSet
