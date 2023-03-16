from typing import Any, Dict

from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet, Q
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from api.models.Document import Document
from api.models.User import User
from api.policies import is_user_internal, get_access_policy_statements
from api.policies.CustomAccessPolicy import CustomAccessPolicy


class DocumentAccessPolicy(CustomAccessPolicy):
    statements = get_access_policy_statements("user_works_for_employer")

    @classmethod
    def scope_queryset(cls, request: Request, queryset: QuerySet[Document]) -> QuerySet[Document]:
        if isinstance(request.user, AnonymousUser) or not isinstance(request.user, User):
            return queryset.none()

        if is_user_internal(request.user):
            return queryset

        request_employer_id = request.user.person.employer.id
        document_access_query = Q(
            Q(buyer__employer__id=request_employer_id)
            | Q(product__supplier__employer__id=request_employer_id)
            | Q(contract__business_deal__buyer__employer__id=request_employer_id)
            | Q(contract__business_deal__supplier__employer__id=request_employer_id)
            | Q(supplier__employer__id=request_employer_id)
        )

        return queryset.filter(document_access_query)

    def user_works_for_employer(
        self, request: Request, view: ModelViewSet, action: str, **kwargs: Dict[str, Any]
    ) -> bool:
        document: Document = view.get_object()
        if isinstance(request.user, AnonymousUser) or not isinstance(request.user, User):
            return False
        return self.scope_queryset(request, queryset=Document.objects.all()).filter(id=document.id).exists()
