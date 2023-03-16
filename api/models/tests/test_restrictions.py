import pytest

from django.db import IntegrityError

from api.models.fixtures import (
    TypeEmployerCoverageGroupFactory,
    TypeEmployerDepartmentFactory,
    TypeEmployerGeographyFactory,
    TypeCoverageGroupRestrictionFactory,
    TypeDepartmentRestrictionFactory,
    TypeGeographyRestrictionFactory,
    TypeSubscriptionFactory,
)


@pytest.mark.django_db
class TestCoverageGroupRestrictionUniqueConstraint:
    def test_duplicate_record_raises_integrity_error(
        self, coverage_group_restriction_factory: TypeCoverageGroupRestrictionFactory
    ) -> None:
        coverage_group_restriction_factory()
        with pytest.raises(IntegrityError):
            coverage_group_restriction_factory()

    def test_can_add_same_subscription_different_mapping(
        self,
        coverage_group_restriction_factory: TypeCoverageGroupRestrictionFactory,
        employer_coverage_group_factory: TypeEmployerCoverageGroupFactory,
    ) -> None:
        coverage_group_restriction_factory()
        coverage_group_restriction_factory(employer_coverage_group=employer_coverage_group_factory())

    def test_can_add_same_mapping_different_subscription(
        self,
        coverage_group_restriction_factory: TypeCoverageGroupRestrictionFactory,
        subscription_factory: TypeSubscriptionFactory,
    ) -> None:
        coverage_group_restriction_factory()
        coverage_group_restriction_factory(subscription=subscription_factory())


@pytest.mark.django_db
class TestDepartmentRestrictionUniqueConstraint:
    def test_duplicate_record_raises_integrity_error(
        self, department_restriction_factory: TypeDepartmentRestrictionFactory
    ) -> None:
        department_restriction_factory()
        with pytest.raises(IntegrityError):
            department_restriction_factory()

    def test_can_add_same_subscription_different_mapping(
        self,
        department_restriction_factory: TypeDepartmentRestrictionFactory,
        employer_department_factory: TypeEmployerDepartmentFactory,
    ) -> None:
        department_restriction_factory()
        department_restriction_factory(employer_department=employer_department_factory())

    def test_can_add_same_mapping_different_subscription(
        self,
        department_restriction_factory: TypeDepartmentRestrictionFactory,
        subscription_factory: TypeSubscriptionFactory,
    ) -> None:
        department_restriction_factory()
        department_restriction_factory(subscription=subscription_factory())


@pytest.mark.django_db
class TestGeographyRestrictionUniqueConstraint:
    def test_duplicate_record_raises_integrity_error(
        self, geography_restriction_factory: TypeGeographyRestrictionFactory
    ) -> None:
        geography_restriction_factory()
        with pytest.raises(IntegrityError):
            geography_restriction_factory()

    def test_can_add_same_subscription_different_mapping(
        self,
        geography_restriction_factory: TypeGeographyRestrictionFactory,
        employer_geography_factory: TypeEmployerGeographyFactory,
    ) -> None:
        geography_restriction_factory()
        geography_restriction_factory(employer_geography=employer_geography_factory())

    def test_can_add_same_mapping_different_subscription(
        self,
        geography_restriction_factory: TypeGeographyRestrictionFactory,
        subscription_factory: TypeSubscriptionFactory,
    ) -> None:
        geography_restriction_factory()
        geography_restriction_factory(subscription=subscription_factory())
