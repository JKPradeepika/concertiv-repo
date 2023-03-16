from typing import Callable

import pytest

from api.models.Geography import Geography
from api.models.Subscription import Subscription
from api.models.SubscriptionPOSGeography import SubscriptionPOSGeography

TypeSubscriptionPOSGeographyFactory = Callable[..., SubscriptionPOSGeography]


@pytest.fixture
def subscription_pos_geography_factory(
    geography: Geography, subscription: Subscription
) -> TypeSubscriptionPOSGeographyFactory:
    # Closure
    def create_employer_geography(
        geography: Geography = geography,
        subscription: Subscription = subscription,
    ) -> SubscriptionPOSGeography:
        return SubscriptionPOSGeography.objects.get_or_create(
            geography=geography,
            subscription=subscription,
        )[0]

    return create_employer_geography


@pytest.fixture
def subscription_pos_geography(
    subscription_pos_geography_factory: TypeSubscriptionPOSGeographyFactory,
) -> SubscriptionPOSGeography:
    return subscription_pos_geography_factory()
