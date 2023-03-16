from typing import Any, Callable, Dict, List

import pytest

from api.models.Geography import Geography

TypeGeographyFactory = Callable[..., Geography]


@pytest.fixture
def geography_factory() -> TypeGeographyFactory:
    # Closure
    def create_geography(name: str = "The Good Geography", **kwargs: Dict[str, Any]) -> Geography:
        return Geography.objects.create(name=name, **kwargs)

    return create_geography


@pytest.fixture
def geography(geography_factory: TypeGeographyFactory) -> Geography:
    return geography_factory()


@pytest.fixture
def geographies(geography_factory: TypeGeographyFactory) -> List[Geography]:
    return [
        geography_factory(name="The Good Geography", id=2),
        geography_factory(name="The Bad Geography", id=3),
        geography_factory(name="The Best Geography", id=4),
    ]
