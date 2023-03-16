from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.request import Request

from api.models.User import User
from api.policies import get_access_policy_statements, is_user_internal
from api.policies.CustomAccessPolicy import CustomAccessPolicy


class UserAccessPolicy(CustomAccessPolicy):
    statements = get_access_policy_statements("user_works_for_employer")

    @classmethod
    def scope_queryset(cls, request: Request, queryset: QuerySet[User]) -> QuerySet[User]:
        if isinstance(request.user, AnonymousUser):
            return queryset.none()
        elif isinstance(request.user, User):
            if is_user_internal(request.user):
                return queryset

            return queryset.filter(person__employer__id=request.user.person.employer.id)

    def user_works_for_employer(
        self, request: Request, view: viewsets.ModelViewSet, action: str, **kwargs: Any
    ) -> bool:
        if view.kwargs.get("pk") == "current":
            return True

        if isinstance(request.user, User):
            target_user: User = view.get_object()
            return bool(target_user.person.employer.id == request.user.person.employer.id)

        return False
