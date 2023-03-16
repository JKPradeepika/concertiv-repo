from copy import deepcopy
import json
from typing import Any, Dict

import pytest
from rest_framework import status

from api.models import EmployerDepartment, User
from api.models.fixtures import TypeEmployerDepartmentFactory
from api.viewsets import EmployerDepartmentViewSet
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource


depts_test_resource = ViewSetTestResource(EmployerDepartmentViewSet, "departments-list")


employer_department_post_data: Dict[str, Any] = {
    "name": "GOOD BUSINESS UNIT",
    "employerId": 1,
}


class TestEmployerDepartmentModelPermissions:
    @pytest.mark.django_db
    def test_employer_departments_will_prevent_get_one(
        self, employer_department: EmployerDepartment, concertiv_user_with_no_permissions: User
    ) -> None:
        response = depts_test_resource.request(
            "retrieve", concertiv_user_with_no_permissions, pk=employer_department.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_departments_will_prevent_get_list(self, concertiv_user_with_no_permissions: User) -> None:
        response = depts_test_resource.request("list", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_departments_will_prevent_post(self, concertiv_user_with_no_permissions: User) -> None:
        response = depts_test_resource.request("create", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_departments_will_prevent_delete(
        self, employer_department: EmployerDepartment, concertiv_user_with_no_permissions: User
    ) -> None:
        response = depts_test_resource.request("destroy", concertiv_user_with_no_permissions, pk=employer_department.pk)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_departments_will_prevent_patch(
        self, employer_department: EmployerDepartment, concertiv_user_with_no_permissions: User
    ) -> None:
        response = depts_test_resource.request(
            "partial_update", concertiv_user_with_no_permissions, pk=employer_department.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_departments_will_prevent_put(
        self, employer_department: EmployerDepartment, concertiv_user_with_no_permissions: User
    ) -> None:
        response = depts_test_resource.request("update", concertiv_user_with_no_permissions, pk=employer_department.pk)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestEmployerDepartmentTenancy:
    @pytest.mark.django_db
    def test_employer_departments_get_one_will_return_correct_employer_department(
        self,
        employer_department_factory: TypeEmployerDepartmentFactory,
        user_with_other_buyer: User,
    ) -> None:
        employer_department = employer_department_factory(employer=user_with_other_buyer.person.employer)
        response = depts_test_resource.request("retrieve", user_with_other_buyer, pk=employer_department.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employer_department.id

    @pytest.mark.django_db
    def test_employer_departments_get_one_will_not_return_bad_employer_department(
        self,
        employer_department_factory: TypeEmployerDepartmentFactory,
        user_with_other_buyer: User,
    ) -> None:
        employer_department = employer_department_factory()
        response = depts_test_resource.request("retrieve", user_with_other_buyer, pk=employer_department.pk)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_employer_departments_get_will_return_correct_employer_departments(
        self,
        employer_department_factory: TypeEmployerDepartmentFactory,
        user_with_other_buyer: User,
    ) -> None:
        departments_from_same_company = [
            employer_department_factory(employer=user_with_other_buyer.person.employer),
            employer_department_factory(employer=user_with_other_buyer.person.employer),
        ]
        employer_department_factory()
        response = depts_test_resource.request("list", user_with_other_buyer)
        assert response.data["count"] == len(departments_from_same_company)

    @pytest.mark.django_db
    def test_departments_post_will_create_correct_departments(self, user_with_other_buyer: User) -> None:

        data = deepcopy(employer_department_post_data)
        data.update({"employerId": user_with_other_buyer.person.employer.id})

        response = depts_test_resource.request("create", user_with_other_buyer, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED

    # Uncomment below when Product has edit / patch capabilities
    """
    @pytest.mark.django_db
    def test_employer_departments_patch_will_not_update_forbidden_employer_departments(
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
    def test_departments_delete_will_not_delete_forbidden_departments(
        self, employer_department_factory: TypeEmployerDepartmentFactory, user_with_other_buyer: User
    ) -> None:
        department = employer_department_factory()
        response = depts_test_resource.request("destroy", user_with_other_buyer, pk=department.pk)
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetEmployerDepartment:
    @pytest.mark.django_db
    def test_api_can_list_employer_departments(self, employer_department: EmployerDepartment, user: User) -> None:
        response = depts_test_resource.request("list", user)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == employer_department.pk

    @pytest.mark.django_db
    def test_api_can_fetch_employer_department_by_id(self, employer_department: EmployerDepartment, user: User) -> None:
        response = depts_test_resource.request("retrieve", user, pk=employer_department.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employer_department.id


class TestPostEmployerDepartment:
    @pytest.mark.django_db
    def test_post_department_can_create_department(
        self,
        user_with_other_buyer: User,
    ) -> None:
        data = deepcopy(employer_department_post_data)
        data.update({"employerId": user_with_other_buyer.person.employer.id})
        response = depts_test_resource.request("create", user_with_other_buyer, json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED


class TestPutEmployerDepartment:
    pass
