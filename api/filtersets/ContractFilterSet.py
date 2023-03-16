from django_filters import rest_framework as filters

from api.models.Contract import Contract


class ContractFilterSet(filters.FilterSet):  # type: ignore
    buyerId = filters.NumberFilter(field_name="business_deal__buyer__id")
    contractSeriesId = filters.NumberFilter(field_name="contract_series__id")
    domainId = filters.NumberFilter(field_name="subscriptions__domain")

    class Meta:
        model = Contract
        fields = ["buyerId", "contractSeriesId", "domainId"]
