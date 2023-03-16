from collections import OrderedDict
from datetime import date
from typing import Any, Dict, List, Optional, Type, Union

from django.db import models, transaction
from rest_framework import serializers

from api.models import EmployerCoverageGroup, EmployerDepartment, EmployerGeography, Geography
from api.models import CoverageGroupRestriction, DepartmentRestriction, GeographyRestriction
from api.models.LicensePeriod import LicensePeriod
from api.models.Subscription import Subscription
from api.models.SubscriptionPOSGeography import SubscriptionPOSGeography
from api.serializers.LicensePeriodSerializer import LicensePeriodSerializer
from api.serializers.SimpleSubscriptionSerializer import (
    SimpleSubscriptionSerializer,
    SubscriptionPOSGeographySerializer,
)
from api.serializers.validation_helpers import (
    ContiguousLicensePeriodDateValidator,
    get_nested_instance,
)
from api.helpers import transform_camelcase_to_snakecase


class SubscriptionSerializer(SimpleSubscriptionSerializer):
    # subscriptionId/delete ONLY used when updating/deleting a subscription from a contract
    subscriptionId = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    delete = serializers.BooleanField(write_only=True, required=False)
    licensePeriods = LicensePeriodSerializer(source="licenses_periods", many=True)
    activeLicensePeriod = serializers.SerializerMethodField(method_name="get_active_license_period")

    class Meta(SimpleSubscriptionSerializer.Meta):
        model = Subscription
        fields = SimpleSubscriptionSerializer.Meta.fields + [
            "activeLicensePeriod",
            "subscriptionId",
            "delete",
            "licensePeriods",
        ]
        validators = [ContiguousLicensePeriodDateValidator("subscriptionId")]

    def validate(self, attrs):
        if "subscriptionId" in attrs:
            get_nested_instance(Subscription, "subscriptionId", attrs["subscriptionId"])
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data: OrderedDict[str, Any]) -> Subscription:
        contract = validated_data.pop("contract")
        licenses_periods = validated_data.pop("licenses_periods")
        restrictions: OrderedDict[str, Any] = validated_data.pop("restrictions", default=OrderedDict())
        pos_geographies: List[OrderedDict] = validated_data.pop("pos_geographies", [])

        subscription = Subscription.objects.create(contract=contract, **validated_data)
        self._create_update_delete_license_periods(
            subscription, licenses_periods, "licensePeriodId", is_new_subscription=True
        )
        self._create_delete_restrictions(subscription, restrictions)
        self._create_subscription_pos_geographies(subscription, pos_geographies)
        return subscription

    @transaction.atomic
    def update(self, instance: Subscription, validated_data: OrderedDict[str, Any]) -> Subscription:
        validated_data.pop("contract", None)
        validated_data.pop("product", None)
        license_periods = validated_data.pop("licenses_periods", [])
        restrictions: OrderedDict[str, List[int]] = validated_data.pop("restrictions", default=OrderedDict())
        pos_geographies: List[OrderedDict] = validated_data.pop("pos_geographies", [])

        instance = super().update(instance, validated_data)
        self._create_update_delete_license_periods(instance, license_periods, "licensePeriodId")
        self._create_delete_restrictions(instance, restrictions)
        self._create_delete_subscription_pos_geographies(instance, pos_geographies)
        return instance

    def _create_subscription_pos_geographies(self, instance: Subscription, pos_geographies: List[Geography]) -> None:
        for geography in pos_geographies:
            SubscriptionPOSGeographySerializer().create({"subscription": instance, "geography": geography})

    def _create_delete_subscription_pos_geographies(
        self, instance: Subscription, pos_geographies: List[Geography]
    ) -> None:
        all_pos_geo_ids = []
        for geography in pos_geographies:
            spg, _ = SubscriptionPOSGeography.objects.get_or_create(subscription=instance, geography=geography)
            all_pos_geo_ids.append(spg.id)
        SubscriptionPOSGeography.objects.filter(subscription=instance).exclude(id__in=all_pos_geo_ids).delete()

    def _create_update_delete_license_periods(
        self, instance: Subscription, license_periods: List[Dict], id_key: str, is_new_subscription: bool = False
    ) -> None:
        for license_period_data in license_periods:
            if is_new_subscription and id_key in license_period_data:
                del license_period_data[id_key]

            if id_key not in license_period_data:
                self._create_license_period(instance, license_period_data)
                continue

            if license_period_data.get("delete"):
                self._delete_license_period(id_key, license_period_data)
                continue

            self._update_license_period(id_key, license_period_data)

    def _create_license_period(self, instance: Subscription, data: Dict[str, Any]) -> LicensePeriod:
        data["subscription"] = instance
        return LicensePeriodSerializer().create(data)

    def _update_license_period(self, id_key: str, data: Dict[str, Any]) -> LicensePeriod:
        subscription = get_nested_instance(LicensePeriod, id_key, data[id_key])
        return LicensePeriodSerializer().update(subscription, data)

    def _delete_license_period(self, id_key: str, data: Dict[str, Any]) -> None:
        license_period = get_nested_instance(LicensePeriod, id_key, data[id_key])
        return license_period.delete()

    def _create_delete_restrictions(
        self, subscription: Subscription, restrictions: OrderedDict[str, List[int]]
    ) -> None:
        restriction_specs = {
            "employer_geography_ids": {
                "source_key_name": "employer_geography",
                "model_class": EmployerGeography,
                "restriction_model_class": GeographyRestriction,
            },
            "employer_coverage_group_ids": {
                "source_key_name": "employer_coverage_group",
                "model_class": EmployerCoverageGroup,
                "restriction_model_class": CoverageGroupRestriction,
            },
            "employer_department_ids": {
                "source_key_name": "employer_department",
                "model_class": EmployerDepartment,
                "restriction_model_class": DepartmentRestriction,
            },
        }

        for restriction_key, restriction_details in restriction_specs.items():
            self.create_delete_restrictions_for_model(
                subscription,
                model_class=restriction_details["model_class"],
                id_list=restrictions.get(restriction_key, []),
                restriction_model_class=restriction_details["restriction_model_class"],
            )

    def create_delete_restrictions_for_model(
        self,
        subscription: Subscription,
        model_class: models.Model,
        id_list: List[int],
        restriction_model_class: Type[Union[CoverageGroupRestriction, DepartmentRestriction, GeographyRestriction]],
    ) -> None:
        """
        If restriction matching does not exist for model class id, it is created.
        If restrictions not in the provided list exist, they are deleted.
        """
        model_class_fk_name = transform_camelcase_to_snakecase(model_class.__name__)

        for id in id_list:
            restriction_model_class.objects.get_or_create(
                subscription=subscription,
                **{model_class_fk_name: model_class.objects.get(id=id)},
            )

        restriction_model_class.objects.filter(subscription=subscription).exclude(
            **{f"{model_class_fk_name}_id__in": id_list}
        ).delete()

    def _create_restrictions_of_given_model(
        self,
        subscription: Subscription,
        source_key_name: str,
        model_ids: List[int],
        model_class: Type[models.Model],
        serializer_class: Type[serializers.ModelSerializer],
    ) -> None:
        for model_id in model_ids:
            model_dict = {
                "subscription": subscription,
                source_key_name: get_nested_instance(model_class, source_key_name, model_id),
            }
            serializer_class().create(model_dict)

    @staticmethod
    def get_active_license_period(obj: Subscription) -> Optional[OrderedDict]:
        today = date.today()
        try:
            return LicensePeriodSerializer(
                obj.licenses_periods.filter(start_date__lte=today, end_date__gte=today).earliest("start_date")
            ).data
        except Exception:
            return None
