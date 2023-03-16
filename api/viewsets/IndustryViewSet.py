from django.db.models import QuerySet
from rest_framework import viewsets

from api.models.Industry import Industry
from api.policies import CustomDjangoModelPermissions, IndustryAccessPolicy
from api.serializers.IndustrySerializer import IndustrySerializer


class IndustryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, IndustryAccessPolicy]

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[Industry]:
        queryset = Industry.objects.order_by("id")
        return IndustryAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = IndustrySerializer
