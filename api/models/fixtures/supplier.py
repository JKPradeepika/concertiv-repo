from typing import Any, Callable, Dict, List, Optional

import pytest

from api.constants import SUPPLIER_TYPE_GENERAL
from api.models.fixtures.employer import TypeEmployerFactory
from api.models.Employer import Employer
from api.models.Supplier import Supplier

TypeSupplierFactory = Callable[..., Supplier]


@pytest.fixture
def supplier_factory(employer_factory: TypeEmployerFactory) -> TypeSupplierFactory:
    # Closure
    def create_supplier(
        name: str = "Cheesy Puff Factory",
        description: str = "The best cheese puffs in the world!",
        is_nda_signed: bool = True,
        type: int = SUPPLIER_TYPE_GENERAL,
        url: str = "https://cheesepufffactory.com",
        employer: Optional[Employer] = None,
        **kwargs: Dict[str, Any],
    ) -> Supplier:
        if not employer:
            employer = employer_factory(name)
        return Supplier.objects.create(
            description=description,
            is_nda_signed=is_nda_signed,
            type=type,
            url=url,
            employer=employer,
            **kwargs,
        )

    return create_supplier


@pytest.fixture
def supplier(supplier_factory: TypeSupplierFactory) -> Supplier:
    return supplier_factory()


@pytest.fixture
def suppliers(supplier_factory: TypeSupplierFactory) -> List[Supplier]:
    return [
        supplier_factory(name="Twice Company"),
        supplier_factory(name="Third Company"),
    ]


@pytest.fixture
def supplier_with_id_1(supplier_factory: TypeSupplierFactory) -> Supplier:
    return supplier_factory(name="Hot Puff Factory", id=1)
