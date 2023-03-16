from typing import Callable

import pytest

from api.models.CoverageGroup import CoverageGroup

TypeCoverageGroupFactory = Callable[..., CoverageGroup]


@pytest.fixture
def coverage_group_factory() -> TypeCoverageGroupFactory:
    # Closure
    def create_coverage_group(name: str = "Research") -> CoverageGroup:
        return CoverageGroup.objects.create(name=name)

    return create_coverage_group


@pytest.fixture
def coverage_group(coverage_group_factory: TypeCoverageGroupFactory) -> CoverageGroup:
    return coverage_group_factory()
