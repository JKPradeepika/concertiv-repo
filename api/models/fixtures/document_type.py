from typing import Callable, List

import pytest

from api.models.DocumentType import DocumentType

TypeDocumentTypeFactory = Callable[..., DocumentType]


@pytest.fixture
def document_type_factory() -> TypeDocumentTypeFactory:
    # Closure
    def create_document_type(name: str = "The Good Document") -> DocumentType:
        return DocumentType.objects.create(name=name)

    return create_document_type


@pytest.fixture
def document_type(document_type_factory: TypeDocumentTypeFactory) -> DocumentType:
    return document_type_factory()


@pytest.fixture
def document_types(document_type_factory: TypeDocumentTypeFactory) -> List[DocumentType]:
    return [
        document_type_factory(name="The Good Document"),
        document_type_factory(name="The Bad Document"),
        document_type_factory(name="The Ugly Document"),
    ]
