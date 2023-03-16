from typing import Any

from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from api.models.User import User
from api.policies import CustomDjangoModelPermissions, UserAccessPolicy
from api.serializers.UserSerializer import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, UserAccessPolicy]

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[User]:
        queryset = User.objects.prefetch_related(
            "person",
            "person__employer",
            "person__employee",
            "person__employee__employer_cost_center",
            "person__employee__employer_employee_level",
            "person__employee__employer_coverage_group",
            "person__employee__employer_department",
            "person__employee__employer_geography",
        )
        return UserAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = UserSerializer

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        A custom version of the `retrieve` method that returns the current user
        if the `pk` is set to `current` (which means the url path was `/users/current`).
        """
        if kwargs.get("pk") == "current":
            return Response(self.get_serializer(request.user).data)

        return super().retrieve(request, args, kwargs)
