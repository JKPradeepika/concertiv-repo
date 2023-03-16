from typing import Callable

import pytest

from api.models import DocumentType, Buyer, Contract, Product, Supplier
from api.models.Document import Document

TypeDocumentFactory = Callable[..., Document]


@pytest.fixture
def document_factory(
    document_type: DocumentType, buyer: Buyer, contract: Contract, product: Product, supplier: Supplier
) -> TypeDocumentFactory:
    # Closure
    def create_document(
        name: str = "Research",
        notes: str = "Notes",
        type: DocumentType = document_type,
        buyer: Buyer = buyer,
        contract: Contract = contract,
        product: Product = product,
        supplier: Supplier = supplier,
    ) -> Document:
        return Document.objects.create(
            name=name,
            buyer=buyer,
            contract=contract,
            product=product,
            supplier=supplier,
            type=type,
            notes=notes,
        )

    return create_document


@pytest.fixture
def document(document_factory: TypeDocumentFactory) -> Document:
    return document_factory()
