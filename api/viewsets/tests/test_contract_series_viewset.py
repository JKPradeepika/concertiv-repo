import pytest

from rest_framework import status

from api.models.User import User
from api.models.fixtures import TypeContractFactory
from api.viewsets.ContractSeriesViewSet import ContractSeriesViewSet
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource

contract_series_test_resource = ViewSetTestResource(ContractSeriesViewSet, "contract-series-list")


@pytest.mark.django_db
class TestContractSeriesReadOnlyEndpoint:
    def test_list_contract_series(self, user: User, contract_factory: TypeContractFactory) -> None:
        contract1 = contract_factory()
        contract2 = contract_factory(previous_contract=contract1)

        contract3 = contract_factory()
        contract4 = contract_factory(previous_contract=contract3)

        response = contract_series_test_resource.request("list", user)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK, response.data
        assert response.data["count"] == 2, response.data
        assert response.data["results"][0]["id"] == contract2.contract_series.id, response.data
        assert response.data["results"][0]["contracts"][1]["id"] == contract1.id, response.data
        assert response.data["results"][0]["contracts"][0]["id"] == contract2.id, response.data
        assert response.data["results"][1]["id"] == contract4.contract_series.id, response.data
        assert response.data["results"][1]["contracts"][1]["id"] == contract3.id, response.data
        assert response.data["results"][1]["contracts"][0]["id"] == contract4.id, response.data

    def test_get_contract_series(self, user: User, contract_factory: TypeContractFactory) -> None:
        contract1 = contract_factory()
        contract2 = contract_factory(previous_contract=contract1)
        response = contract_series_test_resource.request("retrieve", user, pk=contract2.contract_series.id)
        print(response.data)
        assert response.data["id"] == contract2.contract_series.id
        assert response.data["contracts"][1]["id"] == contract1.id
        assert response.data["contracts"][0]["id"] == contract2.id
        assert "status" in response.data["contracts"][0]

    def test_not_authenticated(self, contract_factory: TypeContractFactory) -> None:
        contract1 = contract_factory()
        contract2 = contract_factory(previous_contract=contract1)
        response = contract_series_test_resource.request(
            "retrieve", force_auth_user=None, pk=contract2.contract_series.id
        )
        print(response.data, response.status_code)
        assert response.status_code == status.HTTP_403_FORBIDDEN, response.data

    def test_not_authorized(self, user_with_other_buyer: User, contract_factory: TypeContractFactory) -> None:
        contract1 = contract_factory()
        contract2 = contract_factory(previous_contract=contract1)
        response = contract_series_test_resource.request(
            "retrieve", user_with_other_buyer, pk=contract2.contract_series.id
        )
        print(response.data, response.status_code)
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.data
