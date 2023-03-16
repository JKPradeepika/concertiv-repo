from copy import deepcopy
import json
from typing import Any, Dict

import pytest
from rest_framework import status

from api.models import EmployerBusinessUnit, User
from api.models.fixtures import TypeEmployerBusinessUnitFactory
from api.viewsets import EmployerBusinessUnitViewSet
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource


busunits_test_resource = ViewSetTestResource(EmployerBusinessUnitViewSet, "business-units-list")


employer_business_unit_post_data: Dict[str, Any] = {
    "name": "GOOD BUSINESS UNIT",
    "employerId": 1,
}


class TestEmployerBusinessUnitModelPermissions:
    @pytest.mark.django_db
    def test_employer_business_units_will_prevent_get_one(
        self, employer_business_unit: EmployerBusinessUnit, concertiv_user_with_no_permissions: User
    ) -> None:
        response = busunits_test_resource.request(
            "retrieve", concertiv_user_with_no_permissions, pk=employer_business_unit.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_business_units_will_prevent_get_list(self, concertiv_user_with_no_permissions: User) -> None:
        response = busunits_test_resource.request("list", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_business_units_will_prevent_post(self, concertiv_user_with_no_permissions: User) -> None:
        response = busunits_test_resource.request("create", concertiv_user_with_no_permissions)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_business_units_will_prevent_delete(
        self, employer_business_unit: EmployerBusinessUnit, concertiv_user_with_no_permissions: User
    ) -> None:
        response = busunits_test_resource.request(
            "destroy", concertiv_user_with_no_permissions, pk=employer_business_unit.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_business_units_will_prevent_patch(
        self, employer_business_unit: EmployerBusinessUnit, concertiv_user_with_no_permissions: User
    ) -> None:
        # url = reverse("business-units-list")
        # view = EmployerBusinessUnitViewSet.as_view({"patch": "partial_update"})
        # request_factory = APIRequestFactory()
        # request = request_factory.patch(url, kwargs={"pk": employer_business_unit.pk})
        # force_authenticate(request, user=concertiv_user_with_no_permissions)
        # response = view(request, pk=employer_business_unit.id)
        response = busunits_test_resource.request(
            "partial_update", concertiv_user_with_no_permissions, pk=employer_business_unit.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_employer_business_units_will_prevent_put(
        self, employer_business_unit: EmployerBusinessUnit, concertiv_user_with_no_permissions: User
    ) -> None:
        response = busunits_test_resource.request(
            "update", concertiv_user_with_no_permissions, pk=employer_business_unit.pk
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestEmployerBusinessUnitTenancy:
    @pytest.mark.django_db
    def test_employer_business_units_get_one_will_return_correct_employer_business_unit(
        self,
        employer_business_unit_factory: TypeEmployerBusinessUnitFactory,
        user_with_other_buyer: User,
    ) -> None:
        employer_business_unit = employer_business_unit_factory(employer=user_with_other_buyer.person.employer)
        response = busunits_test_resource.request("retrieve", user_with_other_buyer, pk=employer_business_unit.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employer_business_unit.id

    @pytest.mark.django_db
    def test_employer_business_units_get_one_will_not_return_bad_employer_business_unit(
        self,
        employer_business_unit_factory: TypeEmployerBusinessUnitFactory,
        user_with_other_buyer: User,
    ) -> None:
        employer_business_unit = employer_business_unit_factory()
        response = busunits_test_resource.request("retrieve", user_with_other_buyer, pk=employer_business_unit.pk)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_employer_business_units_get_will_return_correct_employer_business_units(
        self,
        employer_business_unit_factory: TypeEmployerBusinessUnitFactory,
        user_with_other_buyer: User,
    ) -> None:
        business_units_from_same_company = [
            employer_business_unit_factory(employer=user_with_other_buyer.person.employer),
            employer_business_unit_factory(employer=user_with_other_buyer.person.employer),
        ]
        employer_business_unit_factory()
        response = busunits_test_resource.request("list", user_with_other_buyer)
        assert response.data["count"] == len(business_units_from_same_company)

    @pytest.mark.django_db
    def test_business_units_post_will_create_correct_business_units(self, user_with_other_buyer: User) -> None:
        data = deepcopy(employer_business_unit_post_data)
        data.update({"employerId": user_with_other_buyer.person.employer.id})
        response = busunits_test_resource.request("create", user_with_other_buyer, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED

    # Uncomment below when Product has edit / patch capabilities
    """
    @pytest.mark.django_db
    def test_employer_business_units_patch_will_not_update_forbidden_employer_business_units(
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
    def test_business_units_delete_will_not_delete_forbidden_business_units(
        self, employer_business_unit_factory: TypeEmployerBusinessUnitFactory, user_with_other_buyer: User
    ) -> None:
        business_unit = employer_business_unit_factory()
        response = busunits_test_resource.request("destroy", user_with_other_buyer, pk=business_unit.pk)
        print(response.data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetEmployerBusinessUnit:
    @pytest.mark.django_db
    def test_api_can_list_employer_business_units(
        self, employer_business_unit: EmployerBusinessUnit, user: User
    ) -> None:
        response = busunits_test_resource.request("list", user)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == employer_business_unit.pk

    @pytest.mark.django_db
    def test_api_can_fetch_employer_business_unit_by_id(
        self, employer_business_unit: EmployerBusinessUnit, user: User
    ) -> None:
        response = busunits_test_resource.request("retrieve", user, pk=employer_business_unit.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employer_business_unit.id


class TestPostEmployerBusinessUnit:
    @pytest.mark.django_db
    def test_post_business_unit_can_create_business_unit(
        self,
        user_with_other_buyer: User,
    ) -> None:
        data = deepcopy(employer_business_unit_post_data)
        data.update({"employerId": user_with_other_buyer.person.employer.id})
        response = busunits_test_resource.request("create", user_with_other_buyer, json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED


class TestPutEmployerBusinessUnit:
    pass
