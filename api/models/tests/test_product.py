import pytest

from api.models.fixtures import TypeProductFactory, TypeSubscriptionFactory
from api.models.Industry import Industry
from api.models.Product import Product
from api.models.Supplier import Supplier


@pytest.mark.django_db
def test_active_subscriptions_count_is_zero_when_appropriate(
    product_factory: TypeProductFactory,
    industry: Industry,
    supplier: Supplier,
    subscription_expired_factory: TypeSubscriptionFactory,
) -> None:
    # Create a product with zero subscriptions
    product_factory(name="0PRODUCT", industry=industry, supplier=supplier)

    # Create a product with zero active subscriptions (but one expired subscription)
    product_with_one_expired_subscription = product_factory(name="1XPRODUCT", industry=industry, supplier=supplier)
    subscription_expired_factory(product=product_with_one_expired_subscription)

    for product in Product.objects.get_queryset():
        assert product.get_active_subscriptions_count() == 0


@pytest.mark.django_db
def test_active_subscriptions_count_finds_active_subscriptions(
    product_factory: TypeProductFactory,
    industry: Industry,
    supplier: Supplier,
    subscription_active_factory: TypeSubscriptionFactory,
    subscription_expired_factory: TypeSubscriptionFactory,
) -> None:
    # Create a product with zero subscriptions
    product = product_factory(name="1PRODUCT", industry=industry, supplier=supplier)
    subscription_active_factory(product=product)
    subscription_expired_factory(product=product)

    product_annotated = Product.objects.get_queryset().get(name="1PRODUCT")
    assert product_annotated is not None
    assert product_annotated.get_active_subscriptions_count() == 1


@pytest.mark.django_db
def test_active_subscriptions_count_throws_an_error_when_the_product_is_not_annotated(product: Product) -> None:
    with pytest.raises(AttributeError, match=r".*active_subscriptions_count.*"):
        product.get_active_subscriptions_count()
