import pytest

from api.constants import DOMAIN_INSURANCE, DOMAIN_MARKET_DATA
from api.models.fixtures import TypeProductFactory, TypeSubscriptionFactory


@pytest.mark.django_db
class TestSubscriptionDomainIsProductDomain:
    def test_subscription_domain_is_product_domain(
        self, product_factory: TypeProductFactory, subscription_factory: TypeSubscriptionFactory
    ) -> None:
        product = product_factory(domain=DOMAIN_INSURANCE)
        subscription = subscription_factory(product=product, domain=DOMAIN_MARKET_DATA)
        assert subscription.domain == DOMAIN_INSURANCE
