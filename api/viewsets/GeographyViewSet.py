from django.db.models import QuerySet
from rest_framework import viewsets

from api.filtersets import GeographyFilterSet
from api.models.Geography import Geography
from api.policies import CustomDjangoModelPermissions, GeographyAccessPolicy
from api.serializers.GeographySerializer import GeographySerializer


class GeographyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, GeographyAccessPolicy]
    filterset_class = GeographyFilterSet

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[Geography]:
        queryset = Geography.objects.order_by("name")
        return GeographyAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = GeographySerializer
