from typing import Dict, OrderedDict, Optional

from djmoney.contrib.django_rest_framework import MoneyField
from djmoney.money import Money
from djmoney.utils import MONEY_CLASSES
from rest_framework import serializers

from api.constants import (
    LICENSES_PERIODS_STATUSES,
    LICENSES_PERIODS_TYPES,
    LICENSE_PERIODS_TYPES_REQUIREMENTS,
    LICENSES_PERIODS_USAGE_UNITS,
)
from api.models.LicensePeriod import LicensePeriod
from api.models.Subscription import Subscription
from api.serializers.SimpleSubscriptionSerializer import SimpleSubscriptionSerializer
from api.serializers.validation_helpers import get_nested_instance
from api.helpers import transform_camelcase_to_snakecase, ConstantChoiceField


class RenderedMoneyField(MoneyField):
    def to_representation(self, obj):
        if isinstance(obj, MONEY_CLASSES):
            return str(obj)
        return super().to_representation(obj)


class LicensePeriodSerializer(serializers.HyperlinkedModelSerializer):
    # licensePeriodId/delete ONLY used when updating/deleting an existing license period from a subscription/contract
    licensePeriodId = serializers.IntegerField(required=False, write_only=True, allow_null=True)
    delete = serializers.BooleanField(required=False, write_only=True)

    endDate = serializers.DateField(source="end_date")
    exchangeRateToUsdAtTimeOfPurchase = serializers.DecimalField(
        source="exchange_rate_to_usd_at_time_of_purchase",
        max_digits=LicensePeriod._meta.get_field("exchange_rate_to_usd_at_time_of_purchase").max_digits,
        decimal_places=LicensePeriod._meta.get_field("exchange_rate_to_usd_at_time_of_purchase").decimal_places,
        read_only=True,
    )
    incrementalUserPrice = MoneyField(
        source="incremental_user_price",
        max_digits=LicensePeriod._meta.get_field("incremental_user_price").max_digits,
        decimal_places=LicensePeriod._meta.get_field("incremental_user_price").decimal_places,
        required=False,
    )
    incrementalUserPriceCurrency = serializers.CharField(source="incremental_user_price_currency", required=False)
    maxCredits = serializers.IntegerField(source="max_credits", required=False, allow_null=True)
    maxUsers = serializers.IntegerField(source="max_users", required=False, allow_null=True)
    calculatedTotalPrice = serializers.SerializerMethodField(
        method_name="get_calculated_total_price",
        read_only=True,
    )
    price = MoneyField(
        max_digits=LicensePeriod._meta.get_field("price").max_digits,
        decimal_places=LicensePeriod._meta.get_field("price").decimal_places,
    )
    priceCurrency = serializers.CharField(source="price_currency")
    startDate = serializers.DateField(source="start_date", required=False)
    status = ConstantChoiceField(LICENSES_PERIODS_STATUSES, read_only=True, required=False)
    type = ConstantChoiceField(LICENSES_PERIODS_TYPES)
    subscription = SimpleSubscriptionSerializer(read_only=True)
    subscriptionId = serializers.PrimaryKeyRelatedField(
        source="subscription",
        queryset=Subscription.objects.all(),
        write_only=True,
        required=False,
    )
    usageUnit = ConstantChoiceField(
        LICENSES_PERIODS_USAGE_UNITS,
        source="usage_unit",
        required=False,
        allow_null=True,
    )
    usageUnitPrice = MoneyField(
        source="usage_unit_price",
        max_digits=LicensePeriod._meta.get_field("usage_unit_price").max_digits,
        decimal_places=LicensePeriod._meta.get_field("usage_unit_price").decimal_places,
        required=False,
    )
    usageUnitPriceCurrency = serializers.CharField(source="usage_unit_price_currency", required=False)
    proposalPrice = RenderedMoneyField(
        source="proposal_price",
        max_digits=LicensePeriod._meta.get_field("proposal_price").max_digits,
        decimal_places=LicensePeriod._meta.get_field("proposal_price").decimal_places,
        allow_null=True,
        required=False,
    )
    proposalNotes = serializers.CharField(source="proposal_notes", allow_blank=True, required=False)

    @staticmethod
    def get_active_employee_license_count(obj: LicensePeriod) -> int:
        return obj.get_active_employee_license_count()

    @staticmethod
    def get_calculated_total_price(obj: LicensePeriod) -> Money:
        return obj.calculated_total_price

    @staticmethod
    def get_proposal_price(obj: LicensePeriod) -> Optional[Money]:
        return obj.proposal_price

    def _validate_fields_for_license_types(self, data: OrderedDict) -> OrderedDict:
        """
        Ensures that certain license types do have and don't have certain fields.
        Pops forbidden fields from data and raises ValidationError for required fields.
        Note that all keys are snake-cased as this check is being run on transformed request data, not raw.
        """

        updated_license_period: Optional[LicensePeriod] = (
            None
            if not data.get("licensePeriodId")
            else get_nested_instance(LicensePeriod, "licensePeriodId", data["licensePeriodId"])
        )
        if not updated_license_period and not data.get("type") in LICENSE_PERIODS_TYPES_REQUIREMENTS.keys():
            return data
        if not data.get("type"):
            data["type"] = updated_license_period.type

        fields_to_errors: Dict = {}
        required_error_detail = serializers.ErrorDetail(
            string=self.error_messages["required"],
            code="required",
        )

        for field_name in LICENSE_PERIODS_TYPES_REQUIREMENTS[data["type"]]["required"]:
            snakecased_field = transform_camelcase_to_snakecase(field_name)
            if snakecased_field not in data and not getattr(updated_license_period, snakecased_field, None):
                fields_to_errors[field_name] = [required_error_detail]
        for field_name in LICENSE_PERIODS_TYPES_REQUIREMENTS[data["type"]]["invisible"]:
            snakecased_field = transform_camelcase_to_snakecase(field_name)
            if snakecased_field in data:
                data.pop(snakecased_field)
        if fields_to_errors:
            raise serializers.ValidationError(fields_to_errors)

        return data

    def validate(self, attrs: Dict) -> Dict:
        data = super().validate(attrs)
        self._validate_fields_for_license_types(data)
        return data

    class Meta:
        model = LicensePeriod
        fields = [
            "id",
            "licensePeriodId",
            "delete",
            "endDate",
            "exchangeRateToUsdAtTimeOfPurchase",
            "incrementalUserPrice",
            "incrementalUserPriceCurrency",
            "maxCredits",
            "maxUsers",
            "calculatedTotalPrice",
            "price",
            "priceCurrency",
            "startDate",
            "status",
            "subscription",
            "subscriptionId",
            "type",
            "usageUnit",
            "usageUnitPrice",
            "usageUnitPriceCurrency",
            "proposalPrice",
            "proposalNotes",
        ]
