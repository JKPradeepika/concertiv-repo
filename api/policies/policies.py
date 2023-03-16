from typing import Any, List, Optional

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q, QuerySet
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.request import Request

from api.models.User import User


def get_access_policy_statements(
    detail_action_condition: Optional[str] = None,
    create_action_condition: Optional[str] = None,
) -> List[Any]:
    return [
        {
            "action": ["*"],
            "principal": ["group:concertiv"],
            "effect": "allow",
        },
        {
            "action": ["destroy", "partial_update", "retrieve", "update"],
            "principal": ["*"],
            "effect": "allow",
            "condition": [detail_action_condition] if detail_action_condition else ["block"],
        },
        {
            "action": ["create"],
            "principal": ["*"],
            "effect": "allow",
            "condition": [create_action_condition] if create_action_condition else ["block"],
        },
        {
            "action": ["list"],
            "principal": ["*"],
            "effect": "allow",
        },
    ]


def is_user_internal(user: User) -> bool:
    return user.groups.filter(name="concertiv").exists()


def restrict_queryset_if_necessary(
    request: Request, queryset: QuerySet[Any], django_employee_business_deal_link: str
) -> QuerySet[Any]:
    if isinstance(request.user, AnonymousUser):
        return queryset.none()
    elif isinstance(request.user, User):
        if is_user_internal(request.user):
            return queryset
        else:
            return restrict_queryset_to_employee_allowed_models(
                request.user, queryset, django_employee_business_deal_link
            )
    return queryset.none()


# Ensure that current user can only see the models they are allowed to see
def restrict_queryset_to_employee_allowed_models(
    user: User, queryset: QuerySet[Any], django_employee_business_deal_link: str
) -> QuerySet[Any]:
    _django_employee_business_deal_link = django_employee_business_deal_link
    if (django_employee_business_deal_link is not None) and not (django_employee_business_deal_link.endswith("__")):
        _django_employee_business_deal_link += "__"

    return queryset.filter(
        Q(**{django_employee_business_deal_link + "buyer__employer__id": user.person.employer.id})
        | Q(**{django_employee_business_deal_link + "supplier__employer__id": user.person.employer.id})
    )


class CustomDjangoModelPermissions(DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }
