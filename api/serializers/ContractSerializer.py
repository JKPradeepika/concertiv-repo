from typing import Any, Dict, List, Optional

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import ErrorDetail, ValidationError

from api.models.BusinessDeal import BusinessDeal
from api.models.Contract import Contract
from api.models.ContractSeries import ContractSeries
from api.models.Subscription import Subscription
from api.models.LicensePeriod import LicensePeriod
from api.serializers.BusinessDealSerializer import BusinessDealSerializer
from api.serializers.SubscriptionSerializer import SubscriptionSerializer
from api.serializers.SimpleContractSerializer import SimpleContractSerializer
from api.serializers.validation_helpers import get_nested_instance


class ContractSerializer(SimpleContractSerializer):
    subscriptions = SubscriptionSerializer(many=True, required=False, allow_empty=True, allow_null=True)

    class Meta(SimpleContractSerializer.Meta):
        model = Contract
        fields = SimpleContractSerializer.Meta.fields + [
            "subscriptions",
        ]

    def run_validation(self, data: Dict):
        if not self.root.partial:
            data = self._clean_child_ids_for_create_contract_data_validation(data)
        return super().run_validation(data)

    @staticmethod
    def _clean_child_ids_for_create_contract_data_validation(data: Dict) -> Dict:
        for subscription_dict in data.get("subscriptions", []):
            subscription_dict.pop("subscriptionId", None)
            for lp_dict in subscription_dict.get("licensePeriods", subscription_dict.get("licenses_periods", [])):
                lp_dict.pop("licensePeriodId", None)
        return data

    def get_or_create_business_deal_instance(self, validated_data: Dict[str, Any]) -> BusinessDeal:
        if "id" not in validated_data["business_deal"]:
            return BusinessDealSerializer().create(validated_data["business_deal"])

        return get_nested_instance(BusinessDeal, "businessDealId", validated_data["business_deal"]["id"])

    def get_or_create_contract_series_instance(self, validated_data: Dict[str, Any]) -> Optional[ContractSeries]:
        if validated_data.get("previous_contract") is None:
            return None

        previous_contract: Contract = validated_data["previous_contract"]
        if previous_contract.contract_series is None:
            previous_contract.contract_series = ContractSeries.objects.create()
            previous_contract.save()
        return previous_contract.contract_series

    def _validate_all_license_period_currencies_are_same(self, contract: Contract) -> None:
        """Assumes a completely saved contract."""
        license_periods = LicensePeriod.objects.filter(subscription__contract=contract)
        currency = None
        for lp in license_periods:
            if currency is None:
                currency = lp.price.currency
                continue
            if lp.price.currency != currency:
                raise ValidationError(
                    {
                        "non_field_errors": [
                            ErrorDetail(
                                string=_("All license period currencies on contract must be the same."),
                                code="invalid",
                            )
                        ]
                    }
                )

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> Contract:
        validated_data["business_deal"] = self.get_or_create_business_deal_instance(validated_data)
        validated_data["contract_series"] = self.get_or_create_contract_series_instance(validated_data)
        subscriptions: List[Dict] = validated_data.pop("subscriptions")
        contract = Contract.objects.create(**validated_data)
        for subscription in subscriptions:
            subscription["contract"] = contract
            subscription.pop("subscriptionId", None)
            SubscriptionSerializer().create(subscription)
        self._validate_all_license_period_currencies_are_same(contract)
        return contract

    @transaction.atomic
    def update(self, instance, validated_data: Dict[str, Any]):
        validated_data.pop("previous_contract", None)  # don't allow updating whether a contract was a renewal
        validated_data.pop("business_deal", None)  # don't allow updating business deal data
        subscriptions: List[Dict[str, Any]] = validated_data.pop("subscriptions", [])

        instance = super().update(instance, validated_data)
        self._create_update_delete_subscriptions(instance, subscriptions, "subscriptionId")
        self._validate_all_license_period_currencies_are_same(instance)
        return instance

    def _create_update_delete_subscriptions(
        self, instance: Contract, subscription_data_list: List[Dict], id_key: str
    ) -> None:
        for subscription_data in subscription_data_list:
            if id_key not in subscription_data:
                self._create_subscription(instance, subscription_data)
                continue

            if subscription_data.get("delete"):
                self._delete_subscription(id_key, subscription_data)
                continue

            self._update_subscription(id_key, subscription_data)

    def _create_subscription(self, instance: Contract, data: Dict[str, Any]) -> Subscription:
        data["contract"] = instance
        return SubscriptionSerializer().create(data)

    def _update_subscription(self, id_key: str, data: Dict[str, Any]) -> Subscription:
        subscription = get_nested_instance(Subscription, id_key, data[id_key])
        return SubscriptionSerializer().update(subscription, data)

    def _delete_subscription(self, id_key: str, data: Dict[str, Any]) -> None:
        subscription = get_nested_instance(Subscription, id_key, data[id_key])
        return subscription.delete()
