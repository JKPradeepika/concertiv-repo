from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from rest_framework.request import Request

from api.models.Geography import Geography
from api.models.User import User
from api.policies import get_access_policy_statements
from api.policies.CustomAccessPolicy import CustomAccessPolicy


class GeographyAccessPolicy(CustomAccessPolicy):
    statements = get_access_policy_statements("anyone_can_view")

    @classmethod
    def scope_queryset(cls, request: Request, queryset: QuerySet[Geography]) -> QuerySet[Geography]:
        if isinstance(request.user, AnonymousUser):
            return queryset.none()
        elif isinstance(request.user, User):
            return queryset
