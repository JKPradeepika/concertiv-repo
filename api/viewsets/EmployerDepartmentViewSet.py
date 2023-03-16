from django.db.models import QuerySet
from rest_framework import viewsets

from api.filtersets import EmployerDepartmentFilterSet
from api.models.EmployerDepartment import EmployerDepartment
from api.policies import CustomDjangoModelPermissions, EmployerDepartmentAccessPolicy
from api.serializers.EmployerDepartmentSerializer import EmployerDepartmentSerializer


class EmployerDepartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, EmployerDepartmentAccessPolicy]
    filterset_class = EmployerDepartmentFilterSet

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[EmployerDepartment]:
        queryset = EmployerDepartment.objects.order_by("id")
        return EmployerDepartmentAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = EmployerDepartmentSerializer
