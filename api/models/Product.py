from typing import cast

from django.db import models
from django.db.models import Count, Q, QuerySet
from django.db.models.functions import Now, TruncDate
from django.utils.translation import gettext_lazy as _
from django_stubs_ext import WithAnnotations

from api.constants import PRODUCT_STATUS_ACTIVE, PRODUCT_STATUSES, DOMAINS
from api.mixins import ModelTimeStampMixin
from api.models.AgreementType import AgreementType
from api.models.Contact import Contact
from api.models.Geography import Geography
from api.models.Industry import Industry
from api.models.ProductType import ProductType
from api.models.Supplier import Supplier


class ProductManager(models.Manager["Product"]):
    def get_queryset(self) -> "QuerySet[Product]":
        """Annotates each product with its active_subscriptions_count"""
        query_set: "QuerySet[Product]" = (
            super(ProductManager, self)
            .get_queryset()
            .annotate(
                active_subscriptions_count=Count(
                    "subscription",
                    filter=Q(subscription__start_date__lte=TruncDate(Now()))
                    & (Q(subscription__end_date__isnull=True) | Q(subscription__end_date__gte=TruncDate(Now()))),
                )
            )
        )
        return query_set


class Product(ModelTimeStampMixin, models.Model):
    """
    An item or service purchased by a Buyer and sold by a Supplier.
    Products are linked to Buyers via Subscriptions.

    Args:
        - name (TextField): The name of the product
        - description (TextField): A short summary of the product
        - domain (Constant): The domain to which this product is related with
        - status (Constant): The status of this product
        - types (ManyToMany): The types of this product
        - agreement_type (ForeignKey): The agreement_type of this product is related with
        - supplier (ForeignKey): The company or organization that sells the product
        - industry (ForeignKey): The industry to which the product belongs
        - contacts (ManyToManyField): The contacts associated with the product
    """

    name = models.TextField()
    description = models.TextField(blank=True)
    domain = models.SmallIntegerField(choices=DOMAINS)
    status = models.SmallIntegerField(choices=PRODUCT_STATUSES, default=PRODUCT_STATUS_ACTIVE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="products")
    contacts = models.ManyToManyField(Contact, db_table="product_contacts")
    agreement_type = models.ForeignKey(AgreementType, blank=True, null=True, on_delete=models.SET_NULL)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    url = models.URLField(blank=True)
    # new fields for ManyToMany relation (komodo 410, 412, 418)
    types = models.ManyToManyField(ProductType, db_table="product_types")
    industries = models.ManyToManyField(Industry, db_table="product_industries")
    geographies = models.ManyToManyField(Geography, db_table="product_geographies")

    # Annotate objects explicitly so that we get better typing support when calling Product.objects.*
    objects: models.Manager["Product"] = ProductManager()

    class Meta:
        verbose_name_plural = _("Products")
        db_table = "products"

    def __str__(self) -> str:
        return self.name

    def get_active_subscriptions_count(self) -> int:
        """Returns the number of active subscriptions for this product

        WARNING: This method should only be used for products that have been annotated via
        Product.objects.annotate(). Due to current deficiencies in django-stubs, we need to
        explicitly cast the product to a WithAnnotations[Product] object, meaning that we're
        effectively turning type safety off for this method.

        An AttributeError will be raised if the product has not been annotated with `active_subscriptions_count`
        """
        # to WithAnnotations. Unfortunately, there is a bug preventing us from doing so at the moment.
        # https://github.com/typeddjango/django-stubs/issues/763
        self_with_annotations = cast(WithAnnotations["Product"], self)
        return cast(int, self_with_annotations.active_subscriptions_count)
