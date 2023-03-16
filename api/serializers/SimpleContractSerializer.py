from typing import Dict, List, Optional, OrderedDict

from django.utils.translation import gettext_lazy as _
from djmoney.money import Money
from rest_framework import serializers

from api.constants import CONTRACT_DURATION_UNITS, CONTRACT_STATUSES
from api.models.Buyer import Buyer
from api.models.Contract import Contract
from api.models.Supplier import Supplier
from api.serializers.BuyerSerializer import SimpleBuyerSerializer
from api.serializers.SupplierSerializer import SimpleSupplierSerializer
from api.helpers import transform_camelcase_to_snakecase, ConstantChoiceField
from api.serializers.validation_helpers import get_nested_instance


ERR_MSG_RENEWAL_CYCLE = _("Previous contract must not cause a cycle in renewal chain (e.g. A->A or A->B->A).")
ERR_MSG_RENEWAL_LATEST = _("Must renew a contract from the latest contract renewal period.")


class SimpleContractSerializer(serializers.HyperlinkedModelSerializer):

    autorenewalDeadline = serializers.DateField(source="autorenewal_deadline", required=False, allow_null=True)
    autorenewalDuration = serializers.IntegerField(source="autorenewal_duration", required=False, allow_null=True)
    autorenewalDurationUnit = ConstantChoiceField(
        choices=CONTRACT_DURATION_UNITS,
        source="autorenewal_duration_unit",
        required=False,
        allow_null=True,
    )
    buyer = SimpleBuyerSerializer(source="business_deal.buyer", read_only=True)
    buyerId = serializers.PrimaryKeyRelatedField(
        source="business_deal.buyer", queryset=Buyer.objects.all(), write_only=True
    )
    buyerEntityName = serializers.CharField(source="buyer_entity_name")
    businessDealId = serializers.IntegerField(source="business_deal.id", required=False)
    doesAutorenew = serializers.BooleanField(source="get_does_autorenew", read_only=True)
    startDate = serializers.DateField(source="start_date", read_only=True)
    endDate = serializers.DateField(source="end_date", read_only=True)
    signedDate = serializers.DateField(source="signed_date", required=False, allow_null=True)
    status = ConstantChoiceField(CONTRACT_STATUSES)
    subscriptionIds = serializers.PrimaryKeyRelatedField(source="subscriptions", many=True, read_only=True)
    supplier = SimpleSupplierSerializer(source="business_deal.supplier", read_only=True)
    supplierId = serializers.PrimaryKeyRelatedField(
        source="business_deal.supplier", queryset=Supplier.objects.all(), write_only=True
    )
    terminatedAt = serializers.DateField(source="terminated_at", required=False, allow_null=True)
    precautionaryCancellationDate = serializers.DateField(
        source="precautionary_cancellation_date", required=False, allow_null=True
    )
    calculatedTotalPrice = serializers.SerializerMethodField(read_only=True, method_name="get_calculated_total_price")
    previousContractId = serializers.PrimaryKeyRelatedField(
        source="previous_contract", required=False, allow_null=True, queryset=Contract.objects.all()
    )
    contractSeriesId = serializers.PrimaryKeyRelatedField(
        source="contract_series",
        read_only=True,
        allow_null=True,
    )
    proposalPrice = serializers.SerializerMethodField(
        read_only=True,
        method_name="get_proposal_price",
    )

    def validate(self, attrs: OrderedDict) -> OrderedDict:
        data = super().validate(attrs)
        updating_contract_instance: Optional[Contract] = getattr(self.root, "instance", None)
        if self._is_new_contract_autorenew(data):
            self._validate_is_autorenew(data)
        self._validate_previous_contract(data, instance=updating_contract_instance)
        return data

    def get_calculated_total_price(self, obj: Contract) -> Money:
        return obj.calculated_total_price

    @staticmethod
    def get_proposal_price(obj: Contract) -> Optional[Money]:
        return obj.proposal_price

    @staticmethod
    def get_autorenew_field_names() -> List[str]:
        return [
            "autorenewalDeadline",
            "autorenewalDuration",
            "autorenewalDurationUnit",
            "precautionaryCancellationDate",
        ]

    def _validate_previous_contract(self, data: OrderedDict, instance: Optional[Contract] = None) -> None:
        if not data.get("previous_contract"):
            return

        buyer_id = data["business_deal"]["buyer"].id if not instance else instance.business_deal.buyer.id

        previous_contract: Contract = get_nested_instance(
            Contract,
            "previousContractId",
            data["previous_contract"].id,
            queryset=Contract.objects.filter(business_deal__buyer_id=buyer_id),
        )

        if previous_contract.contract_series is not None and instance is None:
            if previous_contract.contract_series.contract_set.latest("start_date", "id").id != previous_contract.id:
                raise serializers.ValidationError(
                    {"previousContractId": [serializers.ErrorDetail(string=ERR_MSG_RENEWAL_LATEST, code="invalid")]}
                )

        if instance is None:
            return

        renewed_contract_chain = [instance]
        while previous_contract is not None:
            if previous_contract in renewed_contract_chain:
                raise serializers.ValidationError(
                    {"previousContractId": [serializers.ErrorDetail(string=ERR_MSG_RENEWAL_CYCLE, code="invalid")]}
                )
            renewed_contract_chain.append(previous_contract)
            previous_contract = previous_contract.previous_contract

    def _is_new_contract_autorenew(self, data: OrderedDict) -> bool:
        """Returns True if an autorenew field is present."""
        for field_name in self.get_autorenew_field_names():
            if data.get(transform_camelcase_to_snakecase(field_name)):
                return True
        return False

    def _validate_is_autorenew(self, data: OrderedDict) -> None:
        """
        Checks if all required autorenew fields for autorenew contracts are set.
        If not, raises a ValidationError.
        """
        required_field_names = ["autorenewalDeadline", "autorenewalDuration", "autorenewalDurationUnit"]

        fields_to_errors: Dict = {}
        required_error_detail = serializers.ErrorDetail(
            string=self.error_messages["required"],
            code="required",
        )
        null_error_detail = serializers.ErrorDetail(
            string=self.error_messages["null"],
            code="null",
        )

        for field_name in required_field_names:
            snake_cased_field_name = transform_camelcase_to_snakecase(field_name)
            if snake_cased_field_name not in data:
                fields_to_errors[field_name] = [required_error_detail]
            elif data.get(snake_cased_field_name) is None:
                fields_to_errors[field_name] = [null_error_detail]
        if fields_to_errors:
            raise serializers.ValidationError(fields_to_errors)

    class Meta:
        model = Contract
        fields = [
            "id",
            "autorenewalDeadline",
            "autorenewalDuration",
            "autorenewalDurationUnit",
            "buyer",
            "buyerId",
            "buyerEntityName",
            "businessDealId",
            "doesAutorenew",
            "endDate",
            "precautionaryCancellationDate",
            "signedDate",
            "startDate",
            "status",
            "subscriptionIds",
            "supplier",
            "supplierId",
            "terminatedAt",
            "calculatedTotalPrice",
            "previousContractId",
            "contractSeriesId",
            "proposalPrice",
        ]
