from django.db.models import QuerySet
from rest_framework import viewsets

from api.filtersets import EmployerEmployeeLevelFilterSet
from api.models.EmployerEmployeeLevel import EmployerEmployeeLevel
from api.policies import CustomDjangoModelPermissions, EmployerEmployeeLevelAccessPolicy
from api.serializers.EmployerEmployeeLevelSerializer import EmployerEmployeeLevelSerializer


class EmployerEmployeeLevelViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, EmployerEmployeeLevelAccessPolicy]
    filterset_class = EmployerEmployeeLevelFilterSet

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[EmployerEmployeeLevel]:
        queryset = EmployerEmployeeLevel.objects.order_by("id")
        return EmployerEmployeeLevelAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = EmployerEmployeeLevelSerializer
