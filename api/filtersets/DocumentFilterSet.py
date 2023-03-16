from django_filters import rest_framework as filters

from api.models.Document import Document


class DocumentFilterSet(filters.FilterSet):
    buyerId = filters.NumberFilter(field_name="buyer_id")
    contractId = filters.NumberFilter(field_name="contract_id")
    productId = filters.NumberFilter(field_name="product_id")
    supplierId = filters.NumberFilter(field_name="supplier_id")
    typeId = filters.NumberFilter(field_name="type_id")

    class Meta:
        model = Document
        fields = ["buyerId", "contractId", "productId", "supplierId"]
