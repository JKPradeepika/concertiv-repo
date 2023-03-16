import pytest
from rest_framework import status

from api.models import Product, User, Subscription
from api.models.fixtures import (
    TypeBusinessDealFactory,
    TypeContractFactory,
    TypeSubscriptionFactory,
)
from api.viewsets.SubscriptionViewSet import SubscriptionViewSet, column_name_mappings
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource

subscription_test_resource = ViewSetTestResource(SubscriptionViewSet, "subscriptions-list")


class TestGetSubscription:
    @pytest.mark.django_db
    def test_get_subscriptions_can_list_subscriptions(
        self,
        business_deal_factory: TypeBusinessDealFactory,
        contract_factory: TypeContractFactory,
        user_with_other_buyer: User,
        subscription_factory: TypeSubscriptionFactory,
        product: Product,
    ) -> None:
        """Test that we can list license periods."""
        business_deal = business_deal_factory(buyer=user_with_other_buyer.person.employer.buyer)
        contract = contract_factory(business_deal=business_deal)
        subscription = subscription_factory(contract, product)
        response = subscription_test_resource.request("list", user_with_other_buyer)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == subscription.pk
        assert response.data["results"][0]["contract"]["id"] == contract.pk

        assert "calculatedTotalPrice" in response.data["results"][0]
        assert "calculatedTotalPricePerUser" in response.data["results"][0]
        assert "activeEmployeeLicenseCount" in response.data["results"][0]
        assert "calculatedTotalPrice" in response.data["results"][0]["contract"]


@pytest.mark.parametrize(
    "filter_column",
    column_name_mappings.keys(),
)
@pytest.mark.django_db
class TestListSubscriptionFilterColumns:
    def test_column_mappings_valid(self, user: User, filter_column: str, subscription: Subscription) -> None:
        response = subscription_test_resource.request(
            "list", user, data={"filterContent": f"{filter_column} equals '1'", "filterOperator": "and"}
        )
        assert response.status_code == status.HTTP_200_OK, response.data
