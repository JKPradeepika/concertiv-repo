from typing import Any, Dict

from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet, Q
from rest_framework import viewsets
from rest_framework.request import Request

from api.models.Contract import ContractSeries
from api.models.User import User
from api.policies import get_access_policy_statements, restrict_queryset_if_necessary
from api.policies.CustomAccessPolicy import CustomAccessPolicy


class ContractSeriesAccessPolicy(CustomAccessPolicy):
    statements = get_access_policy_statements("user_works_for_employer")

    @classmethod
    def scope_queryset(cls, request: Request, queryset: QuerySet[ContractSeries]) -> QuerySet[ContractSeries]:
        return restrict_queryset_if_necessary(request, queryset, "contract__business_deal__")

    def user_works_for_employer(
        self, request: Request, view: viewsets.ModelViewSet, action: str, **kwargs: Dict[str, Any]
    ) -> bool:
        contract_series: ContractSeries = view.get_object()
        if isinstance(request.user, AnonymousUser):
            return False
        if isinstance(request.user, User):
            user_employer = request.user.person.employer
            return contract_series.contract_set.filter(
                Q(business_deal__buyer__employer=user_employer) | Q(business_deal__supplier__employer=user_employer)
            ).exists()
