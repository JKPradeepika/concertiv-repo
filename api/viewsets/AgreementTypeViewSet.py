from django.db.models import QuerySet
from rest_framework import viewsets

from api.models.AgreementType import AgreementType
from api.policies import CustomDjangoModelPermissions, AgreementTypeAccessPolicy
from api.serializers.AgreementTypeSerializer import AgreementTypeSerializer


class AgreementTypeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, AgreementTypeAccessPolicy]

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[AgreementType]:
        queryset = AgreementType.objects.order_by("id")
        return AgreementTypeAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = AgreementTypeSerializer
