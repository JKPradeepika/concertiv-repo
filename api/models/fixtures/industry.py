from typing import Any, Callable, Dict, List

import pytest

from api.constants import DOMAIN_MARKET_DATA
from api.models.Industry import Industry

TypeIndustryFactory = Callable[..., Industry]


@pytest.fixture
def industry_factory() -> TypeIndustryFactory:
    # Closure
    def create_industry(
        name: str = "News",
        domain: str = DOMAIN_MARKET_DATA,
        **kwargs: Dict[str, Any],
    ) -> Industry:
        return Industry.objects.create(name=name, domain=domain, **kwargs)

    return create_industry


@pytest.fixture
def industry(industry_factory: TypeIndustryFactory) -> Industry:
    return industry_factory()


@pytest.fixture
def industries(industry_factory: TypeIndustryFactory) -> List[Industry]:
    return [
        industry_factory(name="Fake News", domain=DOMAIN_MARKET_DATA, id=2),
        industry_factory(name="Tech News", domain=DOMAIN_MARKET_DATA, id=3),
        industry_factory(name="News", domain=DOMAIN_MARKET_DATA, id=4),
    ]
