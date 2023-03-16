from typing import Any, Dict

from rest_access_policy import AccessPolicy
from rest_framework import viewsets
from rest_framework.request import Request


class CustomAccessPolicy(AccessPolicy):  # type: ignore
    def anyone_can_view(
        self, request: Request, view: viewsets.ModelViewSet, action: str, **kwargs: Dict[str, Any]
    ) -> bool:
        return True

    def anyone_can_create(
        self, request: Request, view: viewsets.ModelViewSet, actions: str, **kwargs: Dict[str, Any]
    ) -> bool:
        return True

    def block(self, request: Request, view: viewsets.ModelViewSet, action: str, **kwargs: Dict[str, Any]) -> bool:
        return False
