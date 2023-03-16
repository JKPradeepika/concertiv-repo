from typing import Any, Callable, Dict, List

import pytest

from api.models.AgreementType import AgreementType

TypeAgreementTypeFactory = Callable[..., AgreementType]


@pytest.fixture
def agreement_type_factory() -> TypeAgreementTypeFactory:
    # Closure
    def create_agreement_type(name: str = "The Good Agreement", **kwargs: Dict[str, Any]) -> AgreementType:
        return AgreementType.objects.create(name=name, **kwargs)

    return create_agreement_type


@pytest.fixture
def agreement_type(agreement_type_factory: TypeAgreementTypeFactory) -> AgreementType:
    return agreement_type_factory()


@pytest.fixture
def agreements_types(agreement_type_factory: TypeAgreementTypeFactory) -> List[AgreementType]:
    return [
        agreement_type_factory(name="The Great Agreement", id=1),
        agreement_type_factory(name="The Good Agreement", id=2),
        agreement_type_factory(name="The Bad Agreement", id=3),
        agreement_type_factory(name="The Ugly Agreement", id=4),
    ]
