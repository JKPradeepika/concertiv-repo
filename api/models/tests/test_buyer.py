import pytest

from api.models.Buyer import Buyer
from api.models.fixtures import (
    TypeContactFactory,
    TypeSubscriptionFactory,
)


@pytest.mark.django_db
def test_active_subscriptions_count_is_zero_when_appropriate(
    subscription_expired_factory: TypeSubscriptionFactory,
) -> None:
    subscription_expired_factory()

    for buyer in Buyer.objects.get_queryset():
        assert buyer.get_active_subscriptions_count() == 0


@pytest.mark.django_db
def test_active_subscriptions_count_finds_active_subscriptions(
    subscription_active_factory: TypeSubscriptionFactory,
    subscription_expired_factory: TypeSubscriptionFactory,
) -> None:
    # Create a buyer with one active subscriptions and one expired subscription)
    subscription_active_factory()
    buyer_annotated = Buyer.objects.get_queryset().first()
    assert buyer_annotated is not None
    assert buyer_annotated.get_active_subscriptions_count() == 1

    _ = subscription_expired_factory()

    buyer_annotated = Buyer.objects.get_queryset().first()
    assert buyer_annotated.get_active_subscriptions_count() == 1


@pytest.mark.django_db
def test_active_subscriptions_count_throws_an_error_when_the_buyer_is_not_annotated(buyer: Buyer) -> None:
    with pytest.raises(AttributeError, match=r".*active_subscriptions_count.*"):
        buyer.get_active_subscriptions_count()


@pytest.mark.django_db
def test_contacts_returns_buyer_contacts(buyer: Buyer, contact_factory: TypeContactFactory) -> None:
    buyer_contact = contact_factory(employer=buyer.employer)

    first_result = buyer.contacts.first()
    assert first_result is not None
    assert first_result.id == buyer_contact.id
