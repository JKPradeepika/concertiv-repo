from typing import Any, Dict

from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.request import Request

from api.models.EmployerCostCenter import EmployerCostCenter
from api.models.User import User
from api.policies import get_access_policy_statements, is_user_internal
from api.policies.CustomAccessPolicy import CustomAccessPolicy


class EmployerCostCenterAccessPolicy(CustomAccessPolicy):
    statements = get_access_policy_statements("user_works_for_employer", "anyone_can_create")

    @classmethod
    def scope_queryset(cls, request: Request, queryset: QuerySet[EmployerCostCenter]) -> QuerySet[EmployerCostCenter]:
        if isinstance(request.user, AnonymousUser):
            return queryset.none()
        elif isinstance(request.user, User):
            if is_user_internal(request.user):
                return queryset
            else:
                return queryset.filter(employer__id=request.user.person.employer.id)

        return queryset.none()

    def user_works_for_employer(
        self, request: Request, view: viewsets.ModelViewSet, action: str, **kwargs: Dict[str, Any]
    ) -> bool:
        cost_center: EmployerCostCenter = view.get_object()
        if isinstance(request.user, AnonymousUser):
            return False
        elif isinstance(request.user, User):
            return bool(cost_center.employer.id == request.user.person.employer.id)
