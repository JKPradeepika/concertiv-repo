import datetime
from typing import Callable, Optional

from django.utils import timezone
from moneyed import Money
import pytest

from api.constants import LICENSE_PERIOD_TYPE_OTHER, LICENSE_PERIOD_USAGE_UNIT_OTHER
from api.models.LicensePeriod import LicensePeriod
from api.models.Subscription import Subscription

TypeLicensePeriodFactory = Callable[..., LicensePeriod]

one_year_ago = (timezone.now() - datetime.timedelta(days=365)).date()
one_year_from_now = (timezone.now() + datetime.timedelta(days=365)).date()


@pytest.fixture
def license_period_factory(
    subscription: Optional[Subscription] = None,
    start_date: Optional[datetime.date] = one_year_ago,
    end_date: Optional[datetime.date] = one_year_from_now,
) -> TypeLicensePeriodFactory:
    one_thousand_dollars = Money(1000, "USD")

    # Closure
    def create_license_period(
        subscription: Optional[Subscription] = subscription,  # NOSONAR - 13+ arguments is fine here
        type: int = LICENSE_PERIOD_TYPE_OTHER,
        price: Money = one_thousand_dollars,
        exchange_rate_to_usd_at_time_of_purchase: float = 1,
        start_date: datetime.date = start_date or one_year_ago,
        end_date: datetime.date = end_date or one_year_from_now,
        max_credits: int = 10,
        max_users: int = 10,
        incremental_user_price: Money = one_thousand_dollars,
        usage_unit_price: Money = one_thousand_dollars,
        usage_unit: int = LICENSE_PERIOD_USAGE_UNIT_OTHER,
        **kwargs,
    ) -> LicensePeriod:
        return LicensePeriod.objects.create(
            subscription=subscription,
            type=type,
            price=price,
            exchange_rate_to_usd_at_time_of_purchase=exchange_rate_to_usd_at_time_of_purchase,
            start_date=start_date,
            end_date=end_date,
            max_credits=max_credits,
            max_users=max_users,
            incremental_user_price=incremental_user_price,
            usage_unit_price=usage_unit_price,
            usage_unit=usage_unit,
            **kwargs,
        )

    return create_license_period


@pytest.fixture
def license_period(
    license_period_factory: TypeLicensePeriodFactory,
) -> LicensePeriod:
    return license_period_factory()
