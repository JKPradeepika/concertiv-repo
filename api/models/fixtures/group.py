from typing import Callable

from django.contrib.auth.models import Group
import pytest


TypeGroupFactory = Callable[..., Group]


@pytest.fixture
def group_factory() -> TypeGroupFactory:
    # Closure
    def create_group(
        name: str = "concertiv",
    ) -> Group:
        return Group.objects.create(
            name=name,
        )

    return create_group


@pytest.fixture
def group(group_factory: TypeGroupFactory) -> Group:
    return group_factory()
