from typing import List

from django.db.models import Manager
from rest_framework import serializers

from api.models.Contract import Contract
from api.models.ContractSeries import ContractSeries


class OrderedListSerializer(serializers.ListSerializer):
    def __init__(self, order_by: List[str], *args, **kwargs):
        self.order_by = order_by
        super().__init__(*args, **kwargs)

    def to_representation(self, data):
        iterable = data.order_by(*self.order_by).all() if isinstance(data, Manager) else data

        return [self.child.to_representation(item) for item in iterable]


class ContractSeriesContractItemSerializer(serializers.ModelSerializer):
    startDate = serializers.DateField(source="start_date", read_only=True)
    endDate = serializers.DateField(source="end_date", read_only=True)
    previousContractId = serializers.PrimaryKeyRelatedField(
        source="previous_contract",
        read_only=True,
        allow_null=True,
    )
    contractSeriesId = serializers.PrimaryKeyRelatedField(
        source="contract_series",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Contract
        fields = ["id", "startDate", "endDate", "previousContractId", "contractSeriesId", "status"]


class ContractSeriesSerializer(serializers.ModelSerializer):
    contracts = OrderedListSerializer(
        order_by=["-start_date", "-id"],
        child=ContractSeriesContractItemSerializer(),
        read_only=True,
        source="contract_set",
    )

    class Meta:
        model = ContractSeries
        fields = ["id", "contracts"]
