from rest_framework import serializers

from api.models.BusinessDeal import BusinessDeal
from api.models.Buyer import Buyer
from api.models.Supplier import Supplier
from api.serializers.BuyerSerializer import SimpleBuyerSerializer
from api.serializers.SupplierSerializer import SimpleSupplierSerializer


class BusinessDealSerializer(serializers.HyperlinkedModelSerializer):
    buyer = SimpleBuyerSerializer(read_only=True)
    buyerId = serializers.PrimaryKeyRelatedField(source="buyer", queryset=Buyer.objects.all(), write_only=True)
    supplier = SimpleSupplierSerializer(read_only=True)
    supplierId = serializers.PrimaryKeyRelatedField(source="supplier", queryset=Supplier.objects.all(), write_only=True)

    class Meta:
        model = BusinessDeal
        fields = [
            "id",
            "buyer",
            "buyerId",
            "supplier",
            "supplierId",
        ]
