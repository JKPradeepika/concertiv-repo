from django.db.models import QuerySet
from rest_framework import viewsets

from api.filtersets import EmployerCostCenterFilterSet
from api.models.EmployerCostCenter import EmployerCostCenter
from api.policies import CustomDjangoModelPermissions, EmployerCostCenterAccessPolicy
from api.serializers.EmployerCostCenterSerializer import EmployerCostCenterSerializer


class EmployerCostCenterViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, EmployerCostCenterAccessPolicy]
    filterset_class = EmployerCostCenterFilterSet

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[EmployerCostCenter]:
        queryset = EmployerCostCenter.objects.order_by("id")
        return EmployerCostCenterAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = EmployerCostCenterSerializer
