from typing import Any, Callable, Dict, List

import pytest

from api.constants import DOMAIN_INSURANCE, DOMAIN_MARKET_DATA, DOMAIN_TRAVEL
from api.models.ProductType import ProductType

TypeProductTypeFactory = Callable[..., ProductType]


@pytest.fixture
def product_type_factory() -> TypeProductTypeFactory:
    # Closure
    def create_product_type(
        name: str = "The Good Product", domain: str = DOMAIN_MARKET_DATA, **kwargs: Dict[str, Any]
    ) -> ProductType:
        return ProductType.objects.create(name=name, domain=domain, **kwargs)

    return create_product_type


@pytest.fixture
def product_type(product_type_factory: TypeProductTypeFactory) -> ProductType:
    return product_type_factory()


@pytest.fixture
def product_types(product_type_factory: TypeProductTypeFactory) -> List[ProductType]:
    return [
        product_type_factory(name="The Good Product", domain=DOMAIN_MARKET_DATA, id=2),
        product_type_factory(name="The Bad Product", domain=DOMAIN_INSURANCE, id=3),
        product_type_factory(name="The Ugly Product", domain=DOMAIN_TRAVEL, id=4),
    ]
