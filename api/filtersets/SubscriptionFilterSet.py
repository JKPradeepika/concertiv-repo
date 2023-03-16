from django_filters import rest_framework as filters

from api.models.Subscription import Subscription


class SubscriptionFilterSet(filters.FilterSet):  # type: ignore
    buyerId = filters.NumberFilter(field_name="contract__business_deal__buyer__id")

    class Meta:
        model = Subscription
        fields = ["buyerId"]
