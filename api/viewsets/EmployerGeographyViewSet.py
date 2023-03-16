from django.db.models import QuerySet
from rest_framework import viewsets

from api.filtersets import EmployerGeographyFilterSet
from api.models.EmployerGeography import EmployerGeography
from api.policies import CustomDjangoModelPermissions, EmployerGeographyAccessPolicy
from api.serializers.EmployerGeographySerializer import EmployerGeographySerializer


class EmployerGeographyViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, EmployerGeographyAccessPolicy]
    filterset_class = EmployerGeographyFilterSet

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[EmployerGeography]:
        queryset = EmployerGeography.objects.order_by("id")
        return EmployerGeographyAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = EmployerGeographySerializer
