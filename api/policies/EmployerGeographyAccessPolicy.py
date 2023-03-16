from typing import Any, Dict

from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.request import Request

from api.models.EmployerGeography import EmployerGeography
from api.models.User import User
from api.policies import get_access_policy_statements, is_user_internal
from api.policies.CustomAccessPolicy import CustomAccessPolicy


class EmployerGeographyAccessPolicy(CustomAccessPolicy):
    statements = get_access_policy_statements("user_works_for_employer", "anyone_can_create")

    @classmethod
    def scope_queryset(cls, request: Request, queryset: QuerySet[EmployerGeography]) -> QuerySet[EmployerGeography]:
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
        employer_geography: EmployerGeography = view.get_object()
        if isinstance(request.user, AnonymousUser):
            return False
        elif isinstance(request.user, User):
            return bool(employer_geography.employer.id == request.user.person.employer.id)
