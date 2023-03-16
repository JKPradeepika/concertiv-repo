import pytest

from api.models.fixtures import TypeContactFactory, TypeProductFactory, TypeSupplierFactory
from api.models.Supplier import Supplier


@pytest.mark.django_db
def test_products_count_is_zero_when_appropriate(
    supplier_factory: TypeSupplierFactory,
) -> None:
    # Create a supplier with zero products
    supplier_factory()

    for supplier in Supplier.objects.get_queryset():
        assert supplier.get_products_count() == 0


@pytest.mark.django_db
def test_products_count_finds_products(
    supplier: Supplier,
    product_factory: TypeProductFactory,
) -> None:
    product_factory(supplier=supplier, name="Parmesian Cheese")
    product_factory(supplier=supplier, name="Cheddar Cheese")

    supplier_annotated = Supplier.objects.get_queryset().first()
    assert supplier_annotated is not None
    assert supplier_annotated.get_products_count() == 2


@pytest.mark.django_db
def test_products_count_throws_an_error_when_the_supplier_is_not_annotated(supplier: Supplier) -> None:
    with pytest.raises(AttributeError, match=r".*products_count.*"):
        supplier.get_products_count()


@pytest.mark.django_db
def test_contacts_returns_supplier_contacts(supplier: Supplier, contact_factory: TypeContactFactory) -> None:
    supplier_contact = contact_factory(employer=supplier.employer)

    first_result = supplier.contacts.first()
    assert first_result is not None
    assert first_result.id == supplier_contact.id
