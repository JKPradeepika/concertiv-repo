from django.db.models import QuerySet
from rest_framework import viewsets

from api.filtersets import EmployerBusinessUnitFilterSet
from api.models.EmployerBusinessUnit import EmployerBusinessUnit
from api.policies import CustomDjangoModelPermissions, EmployerBusinessUnitAccessPolicy
from api.serializers.EmployerBusinessUnitSerializer import EmployerBusinessUnitSerializer


class EmployerBusinessUnitViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, EmployerBusinessUnitAccessPolicy]
    filterset_class = EmployerBusinessUnitFilterSet

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[EmployerBusinessUnit]:
        queryset = EmployerBusinessUnit.objects.order_by("id")
        return EmployerBusinessUnitAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = EmployerBusinessUnitSerializer
