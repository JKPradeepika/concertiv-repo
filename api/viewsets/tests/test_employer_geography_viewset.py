from copy import deepcopy
import json
from typing import Any, Dict

import pytest
from rest_framework import status

from api.models import EmployerGeography, User
from api.models.fixtures import TypeEmployerGeographyFactory
from api.viewsets import EmployerGeographyViewSet
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource


geos_test_resource = ViewSetTestResource(EmployerGeographyViewSet, "geographies-list")


employer_geography_post_data: Dict[str, Any] = {
    "name": "GOOD BUSINESS UNIT",
    "employerId": 1,
}


class TestEmployerGeographyModelPermissions:
    @pytest.mark.django_db
    def test_employer_geographys_will_prevent_get_one(
        self, employer_geography: EmployerGeography, concertiv_user_with_no_permissions: User
    ) -> None:
        response = geos_test_resource.request("retrieve", concertiv_user_with_no_permissions, pk=employer_geography.pk)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_geographys_will_prevent_get_list(self, concertiv_user_with_no_permissions: User) -> None:
        response = geos_test_resource.request("list", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_geographys_will_prevent_post(self, concertiv_user_with_no_permissions: User) -> None:
        response = geos_test_resource.request("create", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_geographys_will_prevent_delete(
        self, employer_geography: EmployerGeography, concertiv_user_with_no_permissions: User
    ) -> None:
        response = geos_test_resource.request("destroy", concertiv_user_with_no_permissions, pk=employer_geography.pk)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_geographys_will_prevent_patch(
        self, employer_geography: EmployerGeography, concertiv_user_with_no_permissions: User
    ) -> None:
        response = geos_test_resource.request(
            "partial_update", concertiv_user_with_no_permissions, pk=employer_geography.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_geographys_will_prevent_put(
        self, employer_geography: EmployerGeography, concertiv_user_with_no_permissions: User
    ) -> None:
        response = geos_test_resource.request("update", concertiv_user_with_no_permissions, pk=employer_geography.pk)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestEmployerGeographyTenancy:
    @pytest.mark.django_db
    def test_employer_geographys_get_one_will_return_correct_employer_geography(
        self,
        employer_geography_factory: TypeEmployerGeographyFactory,
        user_with_other_buyer: User,
    ) -> None:
        employer_geography = employer_geography_factory(employer=user_with_other_buyer.person.employer)
        response = geos_test_resource.request("retrieve", user_with_other_buyer, pk=employer_geography.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employer_geography.id

    @pytest.mark.django_db
    def test_employer_geographys_get_one_will_not_return_bad_employer_geography(
        self,
        employer_geography_factory: TypeEmployerGeographyFactory,
        user_with_other_buyer: User,
    ) -> None:
        employer_geography = employer_geography_factory()
        response = geos_test_resource.request("retrieve", user_with_other_buyer, pk=employer_geography.pk)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_employer_geographys_get_will_return_correct_employer_geographys(
        self,
        employer_geography_factory: TypeEmployerGeographyFactory,
        user_with_other_buyer: User,
    ) -> None:
        geographys_from_same_company = [
            employer_geography_factory(employer=user_with_other_buyer.person.employer),
            employer_geography_factory(employer=user_with_other_buyer.person.employer),
        ]
        employer_geography_factory()
        response = geos_test_resource.request("list", user_with_other_buyer)
        assert response.data["count"] == len(geographys_from_same_company)

    @pytest.mark.django_db
    def test_geographys_post_will_create_correct_geographies(self, user_with_other_buyer: User) -> None:
        data = deepcopy(employer_geography_post_data)
        data.update({"employerId": user_with_other_buyer.person.employer.id})
        response = geos_test_resource.request("create", user_with_other_buyer, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED

    # Uncomment below when Product has edit / patch capabilities
    """
    @pytest.mark.django_db
    def test_employer_geographys_patch_will_not_update_forbidden_employer_geographys(
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
    def test_geographys_delete_will_not_delete_forbidden_geographies(
        self, employer_geography_factory: TypeEmployerGeographyFactory, user_with_other_buyer: User
    ) -> None:
        geography = employer_geography_factory()
        response = geos_test_resource.request("destroy", user_with_other_buyer, pk=geography.pk)
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetEmployerGeography:
    @pytest.mark.django_db
    def test_api_can_list_employer_geographies(self, employer_geography: EmployerGeography, user: User) -> None:
        response = geos_test_resource.request("list", user)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == employer_geography.pk

    @pytest.mark.django_db
    def test_api_can_fetch_employer_geography_by_id(self, employer_geography: EmployerGeography, user: User) -> None:
        response = geos_test_resource.request("retrieve", user, pk=employer_geography.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employer_geography.id


class TestPostEmployerGeography:
    @pytest.mark.django_db
    def test_post_geography_can_create_geography(
        self,
        user_with_other_buyer: User,
    ) -> None:
        data = deepcopy(employer_geography_post_data)
        data.update({"employerId": user_with_other_buyer.person.employer.id})
        response = geos_test_resource.request("create", user_with_other_buyer, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED


class TestPutEmployerGeography:
    pass
