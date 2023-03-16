from typing import Any, Dict, Optional

import pytest
from rest_framework import status

from api.models import User
from api.models.fixtures import TypeBuyerFactory
from api.viewsets import BuyerViewSet
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource


buyers_test_resource = ViewSetTestResource(BuyerViewSet, "buyers-list")


@pytest.mark.django_db
class TestViewSetHelpers:
    concertiv_short_code = "CRTV"
    short_code_yabba = "YABBA"
    short_code_dabba = "DABBA"
    short_code_doo = "DOO"

    def test_initial_buyer_list_contains_only_concertiv_buyer(self, user: User) -> None:
        response = buyers_test_resource.request("list", user)
        assert response.status_code == status.HTTP_200_OK
        print(response.data["results"])
        assert response.data["count"] == 1
        assert response.data["results"][0]["shortCode"] == self.concertiv_short_code

    def make_api_request_as_user(self, user: User, request_query_parameters: Optional[Dict[str, str]] = None) -> Any:
        response = buyers_test_resource.request("list", user, data=request_query_parameters)
        return response

    def seed_sample_buyers(self, buyer_factory: TypeBuyerFactory) -> None:
        buyer_factory(short_code=self.short_code_yabba)
        buyer_factory(short_code=self.short_code_dabba)
        buyer_factory(short_code=self.short_code_doo)

    def test_buyer_list_with_added_buyers(self, user: User, buyer_factory: TypeBuyerFactory) -> None:
        self.seed_sample_buyers(buyer_factory)
        response = self.make_api_request_as_user(user)
        assert response.status_code == status.HTTP_200_OK
        print(response.data["results"])
        assert response.data["count"] == 4

    def test_buyer_list_filter_contains(self, user: User, buyer_factory: TypeBuyerFactory) -> None:
        self.seed_sample_buyers(buyer_factory)

        filter_content = "shortcode contains abba"
        filter_operator = "and"
        request_query_params = {
            "filterContent": filter_content,
            "filterOperator": filter_operator,
        }

        response = self.make_api_request_as_user(user, request_query_params)
        assert response.status_code == status.HTTP_200_OK
        print(response.data["results"])
        assert response.data["count"] == 2

    def test_buyer_list_filter_equals(self, user: User, buyer_factory: TypeBuyerFactory) -> None:
        self.seed_sample_buyers(buyer_factory)

        filter_content = f"shortcode equals {self.short_code_yabba}"
        filter_operator = "and"
        request_query_params = {
            "filterContent": filter_content,
            "filterOperator": filter_operator,
        }

        response = self.make_api_request_as_user(user, request_query_params)
        assert response.status_code == status.HTTP_200_OK
        print(response.data["results"])
        assert response.data["count"] == 1

    def test_buyer_list_filter_starts_with(self, user: User, buyer_factory: TypeBuyerFactory) -> None:
        self.seed_sample_buyers(buyer_factory)

        filter_content = "shortcode startswith yab"
        filter_operator = "and"
        request_query_params = {
            "filterContent": filter_content,
            "filterOperator": filter_operator,
        }

        response = self.make_api_request_as_user(user, request_query_params)
        assert response.status_code == status.HTTP_200_OK
        print(response.data["results"])
        assert response.data["count"] == 1

    def test_buyer_list_filter_ends_with(self, user: User, buyer_factory: TypeBuyerFactory) -> None:
        self.seed_sample_buyers(buyer_factory)

        filter_content = "shortcode endswith oo"
        filter_operator = "and"
        request_query_params = {
            "filterContent": filter_content,
            "filterOperator": filter_operator,
        }

        response = self.make_api_request_as_user(user, request_query_params)
        assert response.status_code == status.HTTP_200_OK
        print(response.data["results"])
        assert response.data["count"] == 1

    def test_buyer_list_filter_is_empty(self, user: User, buyer_factory: TypeBuyerFactory) -> None:
        self.seed_sample_buyers(buyer_factory)

        filter_content = "shortcode isempty"
        filter_operator = "and"
        request_query_params = {
            "filterContent": filter_content,
            "filterOperator": filter_operator,
        }

        response = self.make_api_request_as_user(user, request_query_params)
        assert response.status_code == status.HTTP_200_OK
        print(response.data["results"])
        assert response.data["count"] == 0

    def test_buyer_list_filter_is_not_empty(self, user: User, buyer_factory: TypeBuyerFactory) -> None:
        self.seed_sample_buyers(buyer_factory)

        filter_content = "shortcode isnotempty"
        filter_operator = "and"
        request_query_params = {
            "filterContent": filter_content,
            "filterOperator": filter_operator,
        }

        response = self.make_api_request_as_user(user, request_query_params)
        assert response.status_code == status.HTTP_200_OK
        print(response.data["results"])
        assert response.data["count"] == 4

    def test_buyer_list_sort(self, user: User, buyer_factory: TypeBuyerFactory) -> None:
        self.seed_sample_buyers(buyer_factory)

        sort_content = "shortcode desc"
        request_query_params = {"sortContent": sort_content}

        response = self.make_api_request_as_user(user, request_query_params)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 4
        print("results: ", response.data["results"])
        assert response.data["results"][0]["shortCode"] == self.short_code_yabba

    def test_buyer_list_filter_and_sort(self, user: User, buyer_factory: TypeBuyerFactory) -> None:
        self.seed_sample_buyers(buyer_factory)

        filter_content = "shortcode endswith abba"
        filter_operator = "and"
        sort_content = "shortcode desc"
        request_query_params = {
            "filterContent": filter_content,
            "filterOperator": filter_operator,
            "sortContent": sort_content,
        }

        response = self.make_api_request_as_user(user, request_query_params)
        assert response.status_code == status.HTTP_200_OK
        print(response.data["results"])
        assert response.data["count"] == 2
        assert response.data["results"][0]["shortCode"] == self.short_code_yabba
