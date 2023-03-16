from typing import Any, Callable, Dict, List

import pytest

from api.models.BusinessType import BusinessType

TypeBusinessTypeFactory = Callable[..., BusinessType]


@pytest.fixture
def business_type_factory() -> TypeBusinessTypeFactory:
    # Closure
    def create_business_type(name: str = "The Good Agreement", **kwargs: Dict[str, Any]) -> BusinessType:
        return BusinessType.objects.create(name=name, **kwargs)

    return create_business_type


@pytest.fixture
def business_type(business_type_factory: TypeBusinessTypeFactory) -> BusinessType:
    return business_type_factory()


@pytest.fixture
def businesses_types(business_type_factory: TypeBusinessTypeFactory) -> List[BusinessType]:
    return [
        business_type_factory(name="The Good Business", id=2),
        business_type_factory(name="The Bad Business", id=3),
        business_type_factory(name="The Ugly Business", id=4),
    ]
