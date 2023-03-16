import datetime
from typing import Any, Callable, Dict, List, Optional

from django.utils import timezone
import pytest

from api.models.Buyer import Buyer
from api.models.Industry import Industry
from api.models.Geography import Geography
from api.models.fixtures.employer import TypeEmployerFactory

TypeBuyerFactory = Callable[..., Buyer]


@pytest.fixture
def buyer_factory(
    employer_factory: TypeEmployerFactory,
    industry: Industry,
    geography: Geography,
) -> TypeBuyerFactory:
    # Closure
    def create_buyer(
        name: str = "Concertiv, Inc.",
        short_name: str = "Concertiv",
        short_code: str = "CRTV",
        savings_report_frequency_in_months: int = 3,
        first_joined_at: datetime.date = timezone.now().date(),
        termination_date: Optional[datetime.date] = None,
        **kwargs: Dict[str, Any],
    ) -> Buyer:
        employer = employer_factory(name)
        buyer = Buyer.objects.create(
            short_name=short_name,
            short_code=short_code,
            savings_report_frequency_in_months=savings_report_frequency_in_months,
            first_joined_at=first_joined_at,
            termination_date=termination_date,
            employer=employer,
            **kwargs,
        )
        # many to many fields
        buyer.industries.add(industry)
        buyer.geographies.add(geography)
        return buyer

    return create_buyer


@pytest.fixture
def buyer(buyer_factory: TypeBuyerFactory) -> Buyer:
    return buyer_factory()


@pytest.fixture
def buyers(buyer_factory: TypeBuyerFactory) -> List[Buyer]:
    return [
        buyer_factory(name="Twice Company", short_name="TC", short_code="TC"),
        buyer_factory(name="Third Company", short_name="HC", short_code="HC"),
    ]


def buyer2(buyer_factory: TypeBuyerFactory) -> Buyer:
    return buyer_factory(name="Yet Another Company Name", short_name="YACN", short_code="YACN")
