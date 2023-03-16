from typing import Any, Dict
from typing import cast

from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.request import Request

from api.models.Product import Product
from api.models.Supplier import Supplier
from api.models.User import User
from api.policies import get_access_policy_statements
from api.policies.CustomAccessPolicy import CustomAccessPolicy


class ProductAccessPolicy(CustomAccessPolicy):
    statements = get_access_policy_statements("user_works_for_employer", "user_can_create_product")

    @classmethod
    def scope_queryset(cls, request: Request, queryset: QuerySet[Product]) -> QuerySet[Product]:
        if isinstance(request.user, AnonymousUser):
            return queryset.none()
        elif isinstance(request.user, User):
            return queryset

    def user_works_for_employer(
        self, request: Request, view: viewsets.ModelViewSet, action: str, **kwargs: Dict[str, Any]
    ) -> bool:
        product: Product = view.get_object()
        if isinstance(request.user, AnonymousUser):
            return False
        elif isinstance(request.user, User):
            return bool(product.supplier.employer.id == request.user.person.employer.id)

    def user_can_create_product(
        self, request: Request, view: viewsets.ModelViewSet, action: str, **kwargs: Dict[str, Any]
    ) -> bool:
        try:
            supplier: Supplier = Supplier.objects.get(id=cast(int, (request.data.get("supplierId"))))
        except Supplier.DoesNotExist:
            return False
        if isinstance(request.user, AnonymousUser):
            return False
        elif isinstance(request.user, User):
            return bool(supplier.employer.id == request.user.person.employer.id)
