import pytest
from rest_framework import status

from api.models import Geography, User
from api.models.fixtures import TypeGeographyFactory
from api.viewsets import GeographyViewSet
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource

geo_test_resource = ViewSetTestResource(GeographyViewSet, "geographies-list")


@pytest.mark.django_db
class TestGeographyList:
    def test_geography_list(self, user: User, geography: Geography) -> None:
        response = geo_test_resource.request("list", force_auth_user=user)
        assert response.status_code == status.HTTP_200_OK, response.data
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == geography.id

    def test_geography_list_no_auth(self) -> None:
        response = geo_test_resource.request("list", force_auth_user=None)
        assert response.status_code == status.HTTP_403_FORBIDDEN, response.data
        assert response.data["detail"].code == "not_authenticated"

    def test_geography_list_filter_exact_name(self, user: User, geography_factory: TypeGeographyFactory) -> None:
        all_geography_names = ["Bangladesh", "Singapore", "Thailand", "Tahiti"]
        for name in all_geography_names:
            geography_factory(name=name)
        response = geo_test_resource.request("list", user, data={"name": "Tahiti"})
        assert response.status_code == status.HTTP_200_OK, response.data
        assert response.data["count"] == 1, response.data

    def test_geography_list_filter_partial_name(self, user: User, geography_factory: TypeGeographyFactory) -> None:
        all_geography_names = ["Bangladesh", "Singapore", "Thailand", "Tahiti"]
        for name in all_geography_names:
            geography_factory(name=name)
        response = geo_test_resource.request("list", user, data={"name__icontains": "T"})
        assert response.status_code == status.HTTP_200_OK, response.data
        assert response.data["count"] == 3, response.data

    def test_geography_list_filter_exact_id(self, user: User, geography_factory: TypeGeographyFactory) -> None:
        all_geography_names = ["Bangladesh", "Singapore", "Thailand", "Tahiti"]
        geographies = [geography_factory(name=name) for name in all_geography_names]
        response = geo_test_resource.request("list", user, data={"id": geographies[1].id})
        assert response.status_code == status.HTTP_200_OK, response.data
        assert response.data["count"] == 1, response.data
        assert response.data["results"][0]["id"] == geographies[1].id


@pytest.mark.django_db
class TestGeographyGet:
    def test_geography_get(self, user: User, geography: Geography) -> None:
        response = geo_test_resource.request("retrieve", force_auth_user=user, pk=geography.pk)
        assert response.status_code == status.HTTP_200_OK, response.data
        assert response.data["id"] == geography.id

    def test_geography_get_no_auth(self, geography: Geography) -> None:
        response = geo_test_resource.request("retrieve", force_auth_user=None, pk=geography.pk)
        assert response.status_code == status.HTTP_403_FORBIDDEN, response.data
        assert response.data["detail"].code == "not_authenticated"

    def test_geography_get_bad_id(self, user: User, geography: Geography) -> None:
        response = geo_test_resource.request("retrieve", force_auth_user=user, pk=69)
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.data
        assert response.data["detail"] == "Not found."
