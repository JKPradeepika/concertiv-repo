from django.db.models import QuerySet
from rest_framework import viewsets

from api.models.BusinessType import BusinessType
from api.policies import CustomDjangoModelPermissions, BusinessTypeAccessPolicy
from api.serializers.BusinessTypeSerializer import BusinessTypeSerializer


class BusinessTypeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, BusinessTypeAccessPolicy]

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[BusinessType]:
        queryset = BusinessType.objects.order_by("id")
        return BusinessTypeAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = BusinessTypeSerializer
