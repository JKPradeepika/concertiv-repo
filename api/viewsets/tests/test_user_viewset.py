import pytest
from rest_framework import status

from api.models import Supplier, User
from api.models.fixtures import TypeUserFactory
from api.viewsets import UserViewSet
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource

users_test_resource = ViewSetTestResource(UserViewSet, "users-list")


class TestUserModelPermissions:
    @pytest.mark.django_db
    def test_users_will_prevent_get_one(self, concertiv_user_with_no_permissions: User) -> None:
        response = users_test_resource.request(
            "retrieve",
            force_auth_user=concertiv_user_with_no_permissions,
            pk=concertiv_user_with_no_permissions.id,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_buyers_will_prevent_get_list(self, concertiv_user_with_no_permissions: User) -> None:
        response = users_test_resource.request("list", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUserTenancy:
    @pytest.mark.django_db
    def test_users_get_one_will_return_correct_user(self, supplier_user: User) -> None:
        response = users_test_resource.request("retrieve", supplier_user, pk=supplier_user.id)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == supplier_user.id

    @pytest.mark.django_db
    def test_users_get_one_will_not_return_forbidden_user(self, user: User, supplier_user: User) -> None:
        response = users_test_resource.request("retrieve", supplier_user, pk=user.id)
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_users_get_will_return_correct_users(
        self, supplier: Supplier, user_factory: TypeUserFactory, supplier_user: User
    ) -> None:
        users_from_same_company = [
            user_factory(email="bls@bls.com", employer=supplier.employer),
            user_factory(email="cls@cls.com", employer=supplier.employer),
        ]
        user_factory(email="dls@dls.com"),
        user_factory(email="els@els.com"),
        response = users_test_resource.request("list", supplier_user)
        print(response.data)
        assert response.data["count"] == len(users_from_same_company) + 1
        for result in response.data["results"]:
            assert User.objects.get(id=result["id"]).person.employer.id == supplier_user.person.employer.id


class TestGetUser:
    @pytest.mark.django_db
    def test_api_can_list_users(self, user: User) -> None:
        """Test that we can list users"""
        response = users_test_resource.request("list", user)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["email"] == user.email

    @pytest.mark.django_db
    def test_api_can_fetch_user_by_id(self, user: User) -> None:
        """Test that we can fetch a user by ID"""
        response = users_test_resource.request("retrieve", user, pk=user.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    @pytest.mark.django_db
    def test_api_can_fetch_current_user(self, user: User) -> None:
        """Test that we can fetch the current user"""
        response = users_test_resource.request("retrieve", user, pk="current")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email
