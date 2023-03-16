from django.db.models import QuerySet
from rest_framework.request import Request

from api.models.LicensePeriod import LicensePeriod
from api.policies import restrict_queryset_if_necessary
from api.policies.CustomAccessPolicy import CustomAccessPolicy


class LicensePeriodAccessPolicy(CustomAccessPolicy):
    @classmethod
    def scope_queryset(cls, request: Request, queryset: QuerySet[LicensePeriod]) -> QuerySet[LicensePeriod]:
        # return queryset
        return restrict_queryset_if_necessary(request, queryset, "subscription__contract__business_deal__")
