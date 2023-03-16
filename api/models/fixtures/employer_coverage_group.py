from typing import Callable

import pytest

from api.models.CoverageGroup import CoverageGroup
from api.models.Employer import Employer
from api.models.EmployerCoverageGroup import EmployerCoverageGroup

TypeEmployerCoverageGroupFactory = Callable[..., EmployerCoverageGroup]


@pytest.fixture
def employer_coverage_group_factory(
    coverage_group: CoverageGroup, employer: Employer
) -> TypeEmployerCoverageGroupFactory:
    # Closure
    def create_employer_coverage_group(
        coverage_group: CoverageGroup = coverage_group,
        employer: Employer = employer,
        name: str = "Human Resources",
    ) -> EmployerCoverageGroup:
        return EmployerCoverageGroup.objects.create(
            coverage_group=coverage_group,
            employer=employer,
            name=name,
        )

    return create_employer_coverage_group


@pytest.fixture
def employer_coverage_group(employer_coverage_group_factory: TypeEmployerCoverageGroupFactory) -> EmployerCoverageGroup:
    return employer_coverage_group_factory()
