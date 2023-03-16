from typing import Callable

import pytest

from api.models.BusinessDeal import BusinessDeal
from api.models.Buyer import Buyer
from api.models.Supplier import Supplier

TypeBusinessDealFactory = Callable[..., BusinessDeal]


@pytest.fixture
def business_deal_factory(buyer: Buyer, supplier: Supplier) -> TypeBusinessDealFactory:
    # Closure
    def create_business_deal(
        buyer: Buyer = buyer,
        supplier: Supplier = supplier,
    ) -> BusinessDeal:
        return BusinessDeal.objects.create(
            buyer=buyer,
            supplier=supplier,
        )

    return create_business_deal


@pytest.fixture
def business_deal(business_deal_factory: TypeBusinessDealFactory) -> BusinessDeal:
    return business_deal_factory()
