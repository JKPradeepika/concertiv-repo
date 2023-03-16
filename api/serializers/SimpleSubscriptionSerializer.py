from typing import Dict, List, Optional

from django.db.models import Q
from djmoney.money import Money
from rest_framework import serializers

from api.constants import SUBSCRIPTION_BILLING_FREQUENCIES, DISCOUNT_TYPES, IGNORED_CONTRACT_FIELDS_BY_DOMAIN
from api.models.Contract import Contract
from api.models.EmployeeLicense import EmployeeLicense
from api.models.Geography import Geography
from api.models.Product import Product
from api.models.Subscription import Subscription
from api.models.SubscriptionPOSGeography import SubscriptionPOSGeography
from api.models.Supplier import Supplier
from api.serializers.GeographySerializer import GeographySerializer
from api.serializers.ProductSerializer import SimpleProductSerializer
from api.serializers.SimpleContractSerializer import SimpleContractSerializer
from api.serializers.GeographyRestrictionSerializer import GeographyRestrictionSerializer
from api.serializers.DepartmentRestrictionSerializer import DepartmentRestrictionSerializer
from api.serializers.CoverageGroupRestrictionSerializer import CoverageGroupRestrictionSerializer
from api.serializers.RestrictionSerializer import RestrictionSerializer
from api.serializers.SupplierSerializer import SupplierSerializer
from api.helpers import ConstantChoiceField


class SubscriptionPOSGeographySerializer(serializers.ModelSerializer):
    geography = GeographySerializer(read_only=True)

    class Meta:
        model = SubscriptionPOSGeography
        fields = ["geography"]


class SimpleSubscriptionSerializer(serializers.ModelSerializer):
    billingFrequency = ConstantChoiceField(SUBSCRIPTION_BILLING_FREQUENCIES, source="billing_frequency")
    restrictions = RestrictionSerializer(required=False)
    geographyRestrictions = GeographyRestrictionSerializer(many=True, source="geography_restrictions", read_only=True)
    departmentRestrictions = DepartmentRestrictionSerializer(
        many=True, source="department_restrictions", read_only=True
    )
    coverageGroupRestrictions = CoverageGroupRestrictionSerializer(
        many=True, source="coverage_group_restrictions", read_only=True
    )
    contract = SimpleContractSerializer(read_only=True)
    contractId = serializers.PrimaryKeyRelatedField(
        source="contract",
        queryset=Contract.objects.all(),
        write_only=True,
        allow_null=True,
        required=False,
    )
    isMultiterm = serializers.SerializerMethodField()
    name = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)
    product = SimpleProductSerializer(read_only=True)
    productId = serializers.PrimaryKeyRelatedField(
        source="product", queryset=Product.objects.all(), write_only=True, allow_null=False, required=True
    )
    resellerSupplier = SupplierSerializer(source="reseller_supplier", read_only=True, allow_null=True)
    resellerSupplierId = serializers.PrimaryKeyRelatedField(
        source="reseller_supplier", write_only=True, allow_null=True, required=False, queryset=Supplier.objects.all()
    )
    tmcSupplier = SupplierSerializer(source="tmc_supplier", read_only=True, allow_null=True)
    tmcSupplierId = serializers.PrimaryKeyRelatedField(
        source="tmc_supplier", write_only=True, allow_null=True, required=False, queryset=Supplier.objects.all()
    )
    discountType = ConstantChoiceField(source="discount_type", choices=DISCOUNT_TYPES, allow_null=True, required=False)
    startDate = serializers.DateField(source="start_date", read_only=True)
    endDate = serializers.DateField(source="end_date", read_only=True)
    taxRate = serializers.DecimalField(
        source="tax_rate",
        max_digits=Subscription._meta.get_field("tax_rate").max_digits,
        decimal_places=Subscription._meta.get_field("tax_rate").decimal_places,
        allow_null=True,
    )
    contractIsNull = serializers.BooleanField(source="contract_is_null", read_only=True)
    activeEmployeeLicenseCount = serializers.SerializerMethodField(
        method_name="get_active_employee_license_count", read_only=True
    )
    calculatedTotalPrice = serializers.SerializerMethodField(method_name="get_calculated_total_price", read_only=True)
    calculatedTotalPricePerUser = serializers.SerializerMethodField(
        method_name="get_calculated_total_price_per_user", read_only=True
    )
    previousSubscriptionIds = serializers.SerializerMethodField(
        read_only=True, method_name="get_previous_subscription_ids"
    )
    posGeographyIds = serializers.ListSerializer(
        child=serializers.PrimaryKeyRelatedField(queryset=Geography.objects.all()),
        write_only=True,
        required=False,
        source="pos_geographies",
    )
    posGeographies = SubscriptionPOSGeographySerializer(many=True, read_only=True, source="pos_geographies")
    domainIgnoredFields = serializers.SerializerMethodField(read_only=True, method_name="get_domain_ignored_fields")
    proposalPrice = serializers.SerializerMethodField(
        read_only=True,
        method_name="get_proposal_price",
    )

    class Meta:
        model = Subscription
        fields = [
            "id",
            "restrictions",
            "geographyRestrictions",
            "coverageGroupRestrictions",
            "departmentRestrictions",
            "billingFrequency",
            "contract",
            "contractId",
            "isMultiterm",
            "name",
            "notes",
            "product",
            "productId",
            "startDate",
            "endDate",
            "taxRate",
            "contractIsNull",
            "activeEmployeeLicenseCount",
            "calculatedTotalPrice",
            "calculatedTotalPricePerUser",
            "previousSubscriptionIds",
            "resellerSupplier",
            "resellerSupplierId",
            "tmcSupplier",
            "tmcSupplierId",
            "discountType",
            "posGeographyIds",
            "posGeographies",
            "domainIgnoredFields",
            "proposalPrice",
        ]

    def to_representation(self, instance: Contract) -> Dict:
        rendered_data_dict: Dict = super().to_representation(instance)
        return rendered_data_dict

    @staticmethod
    def get_domain_ignored_fields(obj: Subscription) -> Dict[str, List[str]]:
        return IGNORED_CONTRACT_FIELDS_BY_DOMAIN.get(obj.domain, {})

    @staticmethod
    def get_isMultiterm(obj: Subscription) -> bool:
        term_count = obj.licenses_periods.count()
        return term_count > 1

    @staticmethod
    def get_previous_subscription_ids(obj: Subscription) -> List[int]:
        if not obj.contract.previous_contract:
            return None
        return list(
            obj.contract.previous_contract.subscriptions.filter(product=obj.product).values_list("id", flat=True)
        )

    @staticmethod
    def get_calculated_total_price(obj: Subscription) -> Money:
        return obj.calculated_total_price

    @staticmethod
    def get_proposal_price(obj: Subscription) -> Optional[Money]:
        return obj.proposal_price

    def get_calculated_total_price_per_user(self, obj: Subscription) -> Money:
        calc_total_price = self.get_calculated_total_price(obj)
        user_count = self.get_active_employee_license_count(obj)
        if not user_count:
            return calc_total_price
        return calc_total_price / user_count

    @staticmethod
    def get_active_employee_license_count(obj: Subscription) -> int:
        """
        Assumes read-only.
        Return count of EmployeeLicenses that overlap with dates of subscription.
        """
        employee_license_qset = EmployeeLicense.objects.filter(subscription=obj)
        if obj.start_date:
            employee_license_qset = employee_license_qset.filter(
                Q(end_date__isnull=True) | Q(end_date__gte=obj.start_date)
            )

        if obj.end_date:
            employee_license_qset = employee_license_qset.filter(
                Q(start_date__isnull=True) | Q(start_date__lte=obj.end_date)
            )
        return employee_license_qset.count()
