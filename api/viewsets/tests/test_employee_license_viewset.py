import pytest
from rest_framework import status

from api.models import Buyer, User, EmployeeLicense
from api.viewsets import EmployeeLicenseViewSet
from api.viewsets.EmployeeLicenseViewSet import column_name_mappings
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource

emplic_test_resource = ViewSetTestResource(EmployeeLicenseViewSet, "employees-licenses-list")


class TestEmployeeLicenseModelPermissions:
    @pytest.mark.django_db
    def test_employees_licenses_will_prevent_get_one(self, concertiv_user_with_no_permissions: User) -> None:
        response = emplic_test_resource.request(
            "retrieve",
            concertiv_user_with_no_permissions,
            pk=concertiv_user_with_no_permissions.person.employer.buyer.id,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employees_licenses_will_prevent_get_list(self, concertiv_user_with_no_permissions: User) -> None:
        response = emplic_test_resource.request("list", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employees_licenses_will_prevent_post(self, concertiv_user_with_no_permissions: User) -> None:
        response = emplic_test_resource.request("create", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employees_licenses_prevent_delete(self, buyer: Buyer, concertiv_user_with_no_permissions: User) -> None:
        response = emplic_test_resource.request(
            "destroy",
            concertiv_user_with_no_permissions,
            pk=concertiv_user_with_no_permissions.person.employer.buyer.id,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employees_licenses_prevent_patch(self, buyer: Buyer, concertiv_user_with_no_permissions: User) -> None:
        response = emplic_test_resource.request(
            "partial_update",
            concertiv_user_with_no_permissions,
            pk=concertiv_user_with_no_permissions.person.employer.buyer.id,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employees_licenses_prevent_put(self, concertiv_user_with_no_permissions: User) -> None:
        response = emplic_test_resource.request(
            "update",
            concertiv_user_with_no_permissions,
            pk=concertiv_user_with_no_permissions.person.employer.buyer.pk,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestListEmployeeLicense:
    @pytest.mark.django_db
    def test_api_can_list_employees_licenses(
        self,
        user: User,
        employee_license: EmployeeLicense,
    ) -> None:
        response = emplic_test_resource.request("list", force_auth_user=user)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == employee_license.pk
        assert "status" in response.data["results"][0]


@pytest.mark.parametrize(
    "filter_column",
    column_name_mappings.keys(),
)
@pytest.mark.django_db
class TestListEmployeeLicenseFilterColumns:
    def test_column_mappings_valid(self, user: User, filter_column: str, employee_license: EmployeeLicense) -> None:
        response = emplic_test_resource.request(
            "list", user, data={"filterContent": f"{filter_column} equals '1'", "filterOperator": "and"}
        )
        assert response.status_code == status.HTTP_200_OK, response.data
