from typing import Any, Callable, Dict

import pytest

from api.constants import DOMAIN_MARKET_DATA
from api.models.AgreementType import AgreementType
from api.models.Geography import Geography
from api.models.Industry import Industry
from api.models.Product import Product
from api.models.ProductType import ProductType
from api.models.Supplier import Supplier

TypeProductFactory = Callable[..., Product]


@pytest.fixture
def product_factory(
    industry: Industry,
    supplier: Supplier,
    product_type: ProductType,
    geography: Geography,
    agreement_type: AgreementType,
    domain: str = DOMAIN_MARKET_DATA,
) -> TypeProductFactory:
    # Closure
    def create_product(
        name: str = "Bloomberg.com",
        description: str = "Web access for Bloomberg news; Finance-focused with Political coverage and Opinion pieces",
        supplier: Supplier = supplier,
        industry: Industry = industry,
        type: ProductType = product_type,
        geography: geography = geography,
        agreement_type: AgreementType = agreement_type,
        domain: str = domain,
        **kwargs: Dict[str, Any],
    ) -> Product:
        prod = Product.objects.create(
            name=name,
            description=description,
            supplier=supplier,
            agreement_type=agreement_type,
            domain=domain,
            **kwargs,
        )
        # many to many fields
        prod.types.add(type)
        prod.industries.add(industry)
        prod.geographies.add(geography)
        return prod

    return create_product


@pytest.fixture
def product(product_factory: TypeProductFactory) -> Product:
    return product_factory()
