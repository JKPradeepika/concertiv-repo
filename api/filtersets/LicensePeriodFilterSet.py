from django_filters import rest_framework as filters

from api.models.LicensePeriod import LicensePeriod


class LicensePeriodFilterSet(filters.FilterSet):  # type: ignore
    buyerId = filters.NumberFilter(field_name="subscription__contract__business_deal__buyer__id")
    domainId = filters.NumberFilter(field_name="subscription__domain")
    productId = filters.NumberFilter(field_name="subscription__product__id")

    class Meta:
        model = LicensePeriod
        fields = ["buyerId", "domainId", "productId"]
