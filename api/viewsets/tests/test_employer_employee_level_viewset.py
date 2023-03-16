from copy import deepcopy
import json
from typing import Any, Dict

import pytest
from rest_framework import status

from api.models import EmployerEmployeeLevel, User
from api.models.fixtures import TypeEmployerEmployeeLevelFactory
from api.viewsets import EmployerEmployeeLevelViewSet
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource


emplvls_test_resource = ViewSetTestResource(EmployerEmployeeLevelViewSet, "employee-levels-list")


employer_employee_level_post_data: Dict[str, Any] = {
    "name": "GOOD EMPLOYEE LEVEL",
    "employerId": 1,
}


class TestEmployerEmployeeLevelModelPermissions:
    @pytest.mark.django_db
    def test_employer_employee_levels_will_prevent_get_one(
        self, employer_employee_level: EmployerEmployeeLevel, concertiv_user_with_no_permissions: User
    ) -> None:
        response = emplvls_test_resource.request(
            "retrieve", concertiv_user_with_no_permissions, pk=employer_employee_level.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_employee_levels_will_prevent_get_list(self, concertiv_user_with_no_permissions: User) -> None:
        response = emplvls_test_resource.request("list", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_employee_levels_will_prevent_post(self, concertiv_user_with_no_permissions: User) -> None:
        response = emplvls_test_resource.request("create", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_employee_levels_will_prevent_delete(
        self, employer_employee_level: EmployerEmployeeLevel, concertiv_user_with_no_permissions: User
    ) -> None:
        response = emplvls_test_resource.request(
            "destroy", concertiv_user_with_no_permissions, pk=employer_employee_level.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_employee_levels_will_prevent_patch(
        self, employer_employee_level: EmployerEmployeeLevel, concertiv_user_with_no_permissions: User
    ) -> None:
        response = emplvls_test_resource.request(
            "partial_update", concertiv_user_with_no_permissions, pk=employer_employee_level.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_employee_levels_will_prevent_put(
        self, employer_employee_level: EmployerEmployeeLevel, concertiv_user_with_no_permissions: User
    ) -> None:
        response = emplvls_test_resource.request(
            "update", concertiv_user_with_no_permissions, pk=employer_employee_level.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestEmployerEmployeeLevelTenancy:
    @pytest.mark.django_db
    def test_employer_employee_levels_get_one_will_return_correct_employer_employee_level(
        self,
        employer_employee_level_factory: TypeEmployerEmployeeLevelFactory,
        user_with_other_buyer: User,
    ) -> None:
        employer_employee_level = employer_employee_level_factory(employer=user_with_other_buyer.person.employer)
        response = emplvls_test_resource.request("retrieve", user_with_other_buyer, pk=employer_employee_level.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employer_employee_level.id

    @pytest.mark.django_db
    def test_employer_employee_levels_get_one_will_not_return_bad_employer_employee_level(
        self,
        employer_employee_level_factory: TypeEmployerEmployeeLevelFactory,
        user_with_other_buyer: User,
    ) -> None:
        employer_employee_level = employer_employee_level_factory()
        response = emplvls_test_resource.request("retrieve", user_with_other_buyer, pk=employer_employee_level.pk)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_employer_employee_levels_get_will_return_correct_employer_employee_levels(
        self,
        employer_employee_level_factory: TypeEmployerEmployeeLevelFactory,
        user_with_other_buyer: User,
    ) -> None:
        employee_levels_from_same_company = [
            employer_employee_level_factory(employer=user_with_other_buyer.person.employer),
            employer_employee_level_factory(employer=user_with_other_buyer.person.employer),
        ]
        employer_employee_level_factory()
        response = emplvls_test_resource.request("list", user_with_other_buyer)
        assert response.data["count"] == len(employee_levels_from_same_company)

    @pytest.mark.django_db
    def test_employee_levels_post_will_create_correct_employee_levels(self, user_with_other_buyer: User) -> None:
        data = deepcopy(employer_employee_level_post_data)
        data.update({"employerId": user_with_other_buyer.person.employer.id})
        response = emplvls_test_resource.request("create", user_with_other_buyer, json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED

    # Uncomment below when Product has edit / patch capabilities
    """
    @pytest.mark.django_db
    def test_employer_employee_levels_patch_will_not_update_forbidden_employer_employee_levels(
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
    def test_employee_levels_delete_will_not_delete_forbidden_employee_levels(
        self, employer_employee_level_factory: TypeEmployerEmployeeLevelFactory, user_with_other_buyer: User
    ) -> None:
        employee_level = employer_employee_level_factory()
        response = emplvls_test_resource.request("destroy", user_with_other_buyer, pk=employee_level.pk)
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetEmployerEmployeeLevel:
    @pytest.mark.django_db
    def test_api_can_list_employer_employee_levels(
        self, employer_employee_level: EmployerEmployeeLevel, user: User
    ) -> None:
        response = emplvls_test_resource.request("list", user)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == employer_employee_level.pk

    @pytest.mark.django_db
    def test_api_can_fetch_employer_employee_level_by_id(
        self, employer_employee_level: EmployerEmployeeLevel, user: User
    ) -> None:
        response = emplvls_test_resource.request("retrieve", user, pk=employer_employee_level.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employer_employee_level.id


class TestPostEmployerEmployeeLevel:
    @pytest.mark.django_db
    def test_post_employee_level_can_create_employee_level(
        self,
        user_with_other_buyer: User,
    ) -> None:
        data = deepcopy(employer_employee_level_post_data)
        data.update({"employerId": user_with_other_buyer.person.employer.id})
        response = emplvls_test_resource.request("create", user_with_other_buyer, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED


class TestPutEmployerEmployeeLevel:
    pass
