from django.db.models import QuerySet
from rest_framework import viewsets

from api.models.ContractSeries import ContractSeries
from api.policies import CustomDjangoModelPermissions, ContractSeriesAccessPolicy
from api.serializers.ContractSeriesSerializer import ContractSeriesSerializer


class ContractSeriesViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, ContractSeriesAccessPolicy]
    serializer_class = ContractSeriesSerializer

    def get_queryset(self) -> QuerySet[ContractSeries]:
        queryset = ContractSeries.objects.prefetch_related("contract_set")
        queryset = ContractSeriesAccessPolicy.scope_queryset(self.request, queryset)
        return queryset.order_by("id")
