from copy import deepcopy
import json
from typing import Any, Dict

import pytest
from rest_framework import status

from api.models import EmployerCoverageGroup, User
from api.models.fixtures import TypeEmployerCoverageGroupFactory
from api.viewsets import EmployerCoverageGroupViewSet
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource


covgrp_test_resource = ViewSetTestResource(EmployerCoverageGroupViewSet, "coverage-groups-list")


employer_coverage_group_post_data: Dict[str, Any] = {
    "name": "GOOD COVERAGE GROUP",
    "employerId": 1,
}


class TestEmployerCoverageGroupModelPermissions:
    @pytest.mark.django_db
    def test_employer_coverage_groups_will_prevent_get_one(
        self, employer_coverage_group: EmployerCoverageGroup, concertiv_user_with_no_permissions: User
    ) -> None:
        response = covgrp_test_resource.request(
            "retrieve", concertiv_user_with_no_permissions, pk=employer_coverage_group.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_coverage_groups_will_prevent_get_list(self, concertiv_user_with_no_permissions: User) -> None:
        response = covgrp_test_resource.request("list", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_coverage_groups_will_prevent_post(self, concertiv_user_with_no_permissions: User) -> None:
        response = covgrp_test_resource.request("create", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_coverage_groups_will_prevent_delete(
        self, employer_coverage_group: EmployerCoverageGroup, concertiv_user_with_no_permissions: User
    ) -> None:
        response = covgrp_test_resource.request(
            "destroy", concertiv_user_with_no_permissions, pk=employer_coverage_group.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_coverage_groups_will_prevent_patch(
        self, employer_coverage_group: EmployerCoverageGroup, concertiv_user_with_no_permissions: User
    ) -> None:
        response = covgrp_test_resource.request(
            "partial_update", concertiv_user_with_no_permissions, pk=employer_coverage_group.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_coverage_groups_will_prevent_put(
        self, employer_coverage_group: EmployerCoverageGroup, concertiv_user_with_no_permissions: User
    ) -> None:
        response = covgrp_test_resource.request(
            "update", concertiv_user_with_no_permissions, pk=employer_coverage_group.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestEmployerCoverageGroupTenancy:
    @pytest.mark.django_db
    def test_employer_coverage_groups_get_one_will_return_correct_employer_coverage_group(
        self,
        employer_coverage_group_factory: TypeEmployerCoverageGroupFactory,
        user_with_other_buyer: User,
    ) -> None:
        employer_coverage_group = employer_coverage_group_factory(employer=user_with_other_buyer.person.employer)
        response = covgrp_test_resource.request("retrieve", user_with_other_buyer, pk=employer_coverage_group.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employer_coverage_group.id

    @pytest.mark.django_db
    def test_employer_coverage_groups_get_one_will_not_return_bad_employer_coverage_group(
        self,
        employer_coverage_group_factory: TypeEmployerCoverageGroupFactory,
        user_with_other_buyer: User,
    ) -> None:
        employer_coverage_group = employer_coverage_group_factory()
        response = covgrp_test_resource.request("retrieve", user_with_other_buyer, pk=employer_coverage_group.pk)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_employer_coverage_groups_get_will_return_correct_employer_coverage_groups(
        self,
        employer_coverage_group_factory: TypeEmployerCoverageGroupFactory,
        user_with_other_buyer: User,
    ) -> None:
        coverage_groups_from_same_company = [
            employer_coverage_group_factory(employer=user_with_other_buyer.person.employer),
            employer_coverage_group_factory(employer=user_with_other_buyer.person.employer),
        ]
        employer_coverage_group_factory()
        response = covgrp_test_resource.request("list", user_with_other_buyer)
        assert response.data["count"] == len(coverage_groups_from_same_company)

    @pytest.mark.django_db
    def test_coverage_groups_post_will_create_correct_coverage_groups(self, user_with_other_buyer: User) -> None:
        data = deepcopy(employer_coverage_group_post_data)
        data.update({"employerId": user_with_other_buyer.person.employer.id})
        response = covgrp_test_resource.request("create", user_with_other_buyer, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED

    # Uncomment below when Product has edit / patch capabilities
    """
    @pytest.mark.django_db
    def test_employer_coverage_groups_patch_will_not_update_forbidden_employer_coverage_groups(
        self, buyer: Buyer, user_with_other_buyer: User, industries: List[Industry]
    ) -> None:
        url = reverse("cost-centers-list")
        view = CostCenterViewSet.ascategoriesIRequestFactory()
        data = deepcopy(buyer_patch_data)
        request = request_factory.patch(
            url,
            data=json.dumps(data),
            content_type="application/json",
            kwargs={"pk": buyer.pk},
        )
        force_authenticate(request, user=user_with_other_buyer)
        response = view(request, pk=buyer.pk)
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    """

    @pytest.mark.django_db
    def test_coverage_groups_delete_will_not_delete_forbidden_coverage_groups(
        self, employer_coverage_group_factory: TypeEmployerCoverageGroupFactory, user_with_other_buyer: User
    ) -> None:
        coverage_group = employer_coverage_group_factory()
        response = covgrp_test_resource.request("destroy", user_with_other_buyer, pk=coverage_group.pk)
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetEmployerCoverageGroup:
    @pytest.mark.django_db
    def test_api_can_list_employer_coverage_groups(
        self, employer_coverage_group: EmployerCoverageGroup, user: User
    ) -> None:
        response = covgrp_test_resource.request("list", user)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == employer_coverage_group.pk

    @pytest.mark.django_db
    def test_api_can_fetch_employer_coverage_group_by_id(
        self, employer_coverage_group: EmployerCoverageGroup, user: User
    ) -> None:
        response = covgrp_test_resource.request("retrieve", user, pk=employer_coverage_group.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employer_coverage_group.id


class TestPostEmployerCoverageGroup:
    @pytest.mark.django_db
    def test_post_coverage_group_can_create_coverage_group(
        self,
        user_with_other_buyer: User,
    ) -> None:
        data = deepcopy(employer_coverage_group_post_data)
        data.update({"employerId": user_with_other_buyer.person.employer.id})
        response = covgrp_test_resource.request("create", user_with_other_buyer, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED


class TestPutEmployerCoverageGroup:
    pass
