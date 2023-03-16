from typing import cast

from django.db import models
from django.db.models import Count, QuerySet
from django.utils.translation import gettext_lazy as _
from django_stubs_ext import WithAnnotations

from api.constants import SUPPLIER_TYPES
from api.mixins import ModelTimeStampMixin
from api.models.Contact import Contact
from api.models.Employer import Employer
from api.models.Person import Person


class SupplierManager(models.Manager["Supplier"]):
    def get_queryset(self) -> "QuerySet[Supplier]":
        """Annotates each supplier with its products_count"""

        query_set: "QuerySet[Supplier]" = (
            super(SupplierManager, self).get_queryset().annotate(products_count=Count("products")).order_by("id")
        )
        return query_set


class Supplier(ModelTimeStampMixin, models.Model):
    """
    A company or organization selling a Product.

    Fields dropped from Profiler:
    - vertical (duplicated in Supplier.products)

    Fields renamed from Profiler:
    - supplier_type (FK) -> types (ManyToMany)

    Args:
        - name (TextField): The name of the Supplier
        - types (ManyToManyField): The type(s) of the Supplier (e.g. `Market Data`). A Supplier can have
            multiple types if it sells Product in different business areas.
    """

    employer = models.OneToOneField(Employer, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    is_nda_signed = models.BooleanField(default=False)
    type = models.SmallIntegerField(choices=SUPPLIER_TYPES)
    url = models.URLField(blank=True)

    # Annotate objects explicitly so that we get better typing support when calling Supplier.objects.*
    objects: models.Manager["Supplier"] = SupplierManager()

    class Meta:
        verbose_name_plural = _("Suppliers")
        db_table = "suppliers"

    def __str__(self) -> str:
        return self.employer.__str__()

    def get_products_count(self) -> int:
        """Returns the number of products for this supplier

        WARNING: This method should only be used for suppliers that have been annotated via
        Supplier.objects.annotate(). Due to current deficiencies in django-stubs, we need to
        explicitly cast the supplier to a WithAnnotations[Supplier] object, meaning that we're
        effectively turning type safety off for this method.

        An AttributeError will be raised if the supplier has not been annotated with `products_count`
        """
        # TODO We should specify which annotations are valid by adding a second type parameter
        # to WithAnnotations. Unfortunately, there is a bug preventing us from doing so at the moment.
        # https://github.com/typeddjango/django-stubs/issues/763
        self_with_annotations = cast(WithAnnotations["Supplier"], self)
        return cast(int, self_with_annotations.products_count)

    @property
    def contacts(self) -> QuerySet[Contact]:
        persons: models.manager.RelatedManager[Person] = self.employer.persons
        return Contact.objects.filter(person__in=persons.all())
