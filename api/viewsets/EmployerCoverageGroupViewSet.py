from django.db.models import QuerySet
from rest_framework import viewsets

from api.filtersets import EmployerCoverageGroupFilterSet
from api.models.EmployerCoverageGroup import EmployerCoverageGroup
from api.policies import CustomDjangoModelPermissions, EmployerCoverageGroupAccessPolicy
from api.serializers.EmployerCoverageGroupSerializer import EmployerCoverageGroupSerializer


class EmployerCoverageGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, EmployerCoverageGroupAccessPolicy]
    filterset_class = EmployerCoverageGroupFilterSet

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[EmployerCoverageGroup]:
        queryset = EmployerCoverageGroup.objects.order_by("id")
        return EmployerCoverageGroupAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = EmployerCoverageGroupSerializer
