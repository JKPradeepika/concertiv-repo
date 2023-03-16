import datetime
from typing import Callable

from django.utils import timezone
import pytest

from api.models.fixtures.license_period import TypeLicensePeriodFactory
from api.models.Contract import Contract
from api.models.Product import Product
from api.models.Subscription import Subscription

TypeSubscriptionFactory = Callable[..., Subscription]


@pytest.fixture
def subscription_factory(contract: Contract, product: Product) -> TypeSubscriptionFactory:
    def create_subscription(
        contract: Contract = contract,
        product: Product = product,
        name: str = product.name,
        domain: str = product.domain,
    ) -> Subscription:
        return Subscription.objects.create(
            contract=contract,
            product=product,
            name=name,
            domain=domain,
        )

    return create_subscription


@pytest.fixture
def subscription_active_factory(
    contract: Contract, product: Product, license_period_factory: TypeLicensePeriodFactory
) -> TypeSubscriptionFactory:
    def create_active_subscription(
        contract: Contract = contract,
        product: Product = product,
        name: str = product.name,
    ) -> Subscription:
        subscription = Subscription.objects.create(
            contract=contract,
            product=product,
            name=name,
        )
        one_year_ago = (timezone.now() - datetime.timedelta(days=365)).date()
        one_year_from_now = (timezone.now() + datetime.timedelta(days=365)).date()
        license_period_factory(subscription=subscription, start_date=one_year_ago, end_date=one_year_from_now)
        return subscription

    return create_active_subscription


@pytest.fixture
def subscription_expired_factory(
    contract: Contract,
    product: Product,
    license_period_factory: TypeLicensePeriodFactory,
) -> TypeSubscriptionFactory:
    def create_expired_subscription(
        contract: Contract = contract,
        product: Product = product,
        name: str = product.name,
    ) -> Subscription:
        subscription = Subscription.objects.create(
            contract=contract,
            product=product,
            name=name,
        )
        one_year_ago = (timezone.now() - datetime.timedelta(days=365)).date()
        two_years_ago = (timezone.now() - datetime.timedelta(days=730)).date()
        license_period_factory(subscription=subscription, start_date=two_years_ago, end_date=one_year_ago)
        return subscription

    return create_expired_subscription


@pytest.fixture
def subscription(subscription_factory: TypeSubscriptionFactory) -> Subscription:
    return subscription_factory()
