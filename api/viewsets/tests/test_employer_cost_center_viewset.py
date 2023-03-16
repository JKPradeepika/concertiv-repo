from copy import deepcopy
import json
from typing import Any, Dict

import pytest
from rest_framework import status

from api.models import EmployerCostCenter, User
from api.models.fixtures import TypeEmployerCostCenterFactory
from api.viewsets import EmployerCostCenterViewSet
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource


costcenters_test_resource = ViewSetTestResource(EmployerCostCenterViewSet, "cost-centers-list")


employer_cost_center_post_data: Dict[str, Any] = {
    "name": "GOOD COST CENTER",
    "employerId": 1,
}


class TestEmployerCostCenterModelPermissions:
    @pytest.mark.django_db
    def test_employer_cost_centers_will_prevent_get_one(
        self, employer_cost_center: EmployerCostCenter, concertiv_user_with_no_permissions: User
    ) -> None:
        response = costcenters_test_resource.request(
            "retrieve", concertiv_user_with_no_permissions, pk=employer_cost_center.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_cost_centers_will_prevent_get_list(self, concertiv_user_with_no_permissions: User) -> None:
        response = costcenters_test_resource.request("list", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_cost_centers_will_prevent_post(self, concertiv_user_with_no_permissions: User) -> None:
        response = costcenters_test_resource.request("create", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_cost_centers_will_prevent_delete(
        self, employer_cost_center: EmployerCostCenter, concertiv_user_with_no_permissions: User
    ) -> None:
        response = costcenters_test_resource.request(
            "destroy", concertiv_user_with_no_permissions, pk=employer_cost_center.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_cost_centers_will_prevent_patch(
        self, employer_cost_center: EmployerCostCenter, concertiv_user_with_no_permissions: User
    ) -> None:
        response = costcenters_test_resource.request(
            "partial_update", concertiv_user_with_no_permissions, pk=employer_cost_center.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_cost_centers_will_prevent_put(
        self, employer_cost_center: EmployerCostCenter, concertiv_user_with_no_permissions: User
    ) -> None:
        response = costcenters_test_resource.request(
            "update", concertiv_user_with_no_permissions, pk=employer_cost_center.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestEmployerCostCenterTenancy:
    @pytest.mark.django_db
    def test_employer_cost_centers_get_one_will_return_correct_employer_cost_center(
        self,
        employer_cost_center_factory: TypeEmployerCostCenterFactory,
        user_with_other_buyer: User,
    ) -> None:
        employer_cost_center = employer_cost_center_factory(employer=user_with_other_buyer.person.employer)
        employer_cost_center_factory()
        response = costcenters_test_resource.request("retrieve", user_with_other_buyer, pk=employer_cost_center.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employer_cost_center.id

    @pytest.mark.django_db
    def test_employer_cost_centers_get_one_will_not_return_bad_employer_cost_center(
        self,
        employer_cost_center_factory: TypeEmployerCostCenterFactory,
        user_with_other_buyer: User,
    ) -> None:
        employer_cost_center = employer_cost_center_factory()
        response = costcenters_test_resource.request("retrieve", user_with_other_buyer, pk=employer_cost_center.pk)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_employer_cost_centers_get_will_return_correct_employer_cost_centers(
        self,
        employer_cost_center_factory: TypeEmployerCostCenterFactory,
        user_with_other_buyer: User,
    ) -> None:
        employer_cost_centers_from_the_same_employer = [
            employer_cost_center_factory(employer=user_with_other_buyer.person.employer)
        ]
        employer_cost_center_factory()
        response = costcenters_test_resource.request("list", user_with_other_buyer)
        assert response.data["count"] == len(employer_cost_centers_from_the_same_employer)

    @pytest.mark.django_db
    def test_employer_cost_centers_post_will_create_correct_employer_cost_centers(
        self, user_with_other_buyer: User
    ) -> None:
        data = deepcopy(employer_cost_center_post_data)
        data.update({"employerId": user_with_other_buyer.person.employer.id})
        response = costcenters_test_resource.request("create", user_with_other_buyer, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED

    # Uncomment below when Product has edit / patch capabilities
    """
    @pytest.mark.django_db
    def test_employer_cost_centers_patch_will_not_update_forbidden_employer_cost_centers(
        self, buyer: Buyer, user_with_other_buyer: User, industries: List[Industry]
    ) -> None:
        url = reverse("cost-centers-list")
        view = EmployerCostCenterViewSet.ascategoriesIRequestFactory()
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
    def test_employer_cost_centers_delete_will_not_delete_forbidden_employer_cost_centers(
        self, employer_cost_center_factory: TypeEmployerCostCenterFactory, user_with_other_buyer: User
    ) -> None:
        employer_cost_center = employer_cost_center_factory()
        response = costcenters_test_resource.request("destroy", user_with_other_buyer, pk=employer_cost_center.pk)
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetEmployerCostCenter:
    @pytest.mark.django_db
    def test_api_can_list_employer_cost_centers(self, employer_cost_center: EmployerCostCenter, user: User) -> None:
        response = costcenters_test_resource.request("list", user)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == employer_cost_center.pk

    @pytest.mark.django_db
    def test_api_can_fetch_employer_cost_center_by_id(
        self, employer_cost_center: EmployerCostCenter, user: User
    ) -> None:
        response = costcenters_test_resource.request("retrieve", user, pk=employer_cost_center.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employer_cost_center.id


class TestPostEmployerCostCenter:
    @pytest.mark.django_db
    def test_post_employer_cost_center_can_create_employer_cost_center(
        self,
        user_with_other_buyer: User,
    ) -> None:
        data = deepcopy(employer_cost_center_post_data)
        data.update({"employerId": user_with_other_buyer.person.employer.id})

        response = costcenters_test_resource.request("create", user_with_other_buyer, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED


class TestPutEmployerCostCenter:
    pass
