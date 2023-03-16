from typing import Callable

import pytest

from api.models.EmployerGeography import EmployerGeography
from api.models.GeographyRestriction import GeographyRestriction
from api.models.Subscription import Subscription

TypeGeographyRestrictionFactory = Callable[..., GeographyRestriction]


@pytest.fixture
def geography_restriction_factory(
    subscription: Subscription, employer_geography: EmployerGeography
) -> TypeGeographyRestrictionFactory:
    # Closure
    def create_geography_restriction(
        subscription: Subscription = subscription,
        employer_geography: EmployerGeography = employer_geography,
    ) -> GeographyRestriction:
        return GeographyRestriction.objects.create(
            subscription=subscription,
            employer_geography=employer_geography,
        )

    return create_geography_restriction


@pytest.fixture
def geography_restriction(
    geography_restriction_factory: TypeGeographyRestrictionFactory,
) -> GeographyRestriction:
    return geography_restriction_factory()
