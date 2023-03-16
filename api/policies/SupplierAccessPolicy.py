from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from rest_framework.request import Request

from api.models.Supplier import Supplier
from api.models.User import User
from api.policies import get_access_policy_statements, is_user_internal
from api.policies.CustomAccessPolicy import CustomAccessPolicy


class SupplierAccessPolicy(CustomAccessPolicy):
    statements = get_access_policy_statements("anyone_can_view")

    @classmethod
    def scope_queryset(cls, request: Request, queryset: QuerySet[Supplier]) -> QuerySet[Supplier]:
        if isinstance(request.user, AnonymousUser) or not isinstance(request.user, User):
            return queryset.none()

        if request._request.method == "GET":
            return queryset

        if is_user_internal(request.user):
            return queryset

        return queryset.filter(employer__id=request.user.person.employer.id)
