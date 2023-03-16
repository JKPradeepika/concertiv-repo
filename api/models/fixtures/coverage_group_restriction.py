from typing import Callable

import pytest

from api.models.CoverageGroupRestriction import CoverageGroupRestriction
from api.models.EmployerCoverageGroup import EmployerCoverageGroup
from api.models.Subscription import Subscription

TypeCoverageGroupRestrictionFactory = Callable[..., CoverageGroupRestriction]


@pytest.fixture
def coverage_group_restriction_factory(
    subscription: Subscription, employer_coverage_group: EmployerCoverageGroup
) -> TypeCoverageGroupRestrictionFactory:
    # Closure
    def create_coverage_group_restriction(
        subscription: Subscription = subscription,
        employer_coverage_group: EmployerCoverageGroup = employer_coverage_group,
    ) -> CoverageGroupRestriction:
        return CoverageGroupRestriction.objects.create(
            subscription=subscription,
            employer_coverage_group=employer_coverage_group,
        )

    return create_coverage_group_restriction


@pytest.fixture
def coverage_group_restriction(
    coverage_group_restriction_factory: TypeCoverageGroupRestrictionFactory,
) -> CoverageGroupRestriction:
    return coverage_group_restriction_factory()
