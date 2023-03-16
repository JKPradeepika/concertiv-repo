"""Common resources to make testing viewsets easier to read and write."""

from io import StringIO
from typing import Any, Dict, Optional

from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.test import override_settings
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.viewsets import ViewSet

DEFAULT_CONTENT_TYPE = "application/json"
DEFAULT_TEST_STORAGE = "api.viewsets.tests.viewset_test_helpers.TestMockStorage"


class TestMockStorage(Storage):
    def __init__(self, *args, **kwargs):
        self.cache = {}

    def _open(self, name: str, *args, **kwargs) -> ContentFile:
        return ContentFile(self.cache.get(name))

    def _save(self, name: str, content: StringIO) -> str:
        content = content.read()

        while name in self.cache:
            name = self.get_available_name(name)
        self.cache[name] = content
        return name

    def exists(self, name: str) -> bool:
        return name in self.cache

    def url(self, name: str) -> str:
        return f"http://faketestserver.local/{name}"


class ViewSetTestResource:
    """Represents a viewset resource that can accept test requests and return responses."""

    def __init__(
        self,
        viewset_class: ViewSet,
        resource_name: Optional[str] = None,
        url: Optional[None] = None,
        override_default_storage: bool = False,
        **req_factory_kwargs,
    ):
        """Specify either url or resource name when initializing."""
        self._resource_name = resource_name
        self._viewset_class = viewset_class
        self.override_default_storage = override_default_storage
        self.url = reverse(self._resource_name) if self._resource_name else url
        self.request_factory = APIRequestFactory(**req_factory_kwargs)

    @property
    def view_methods_to_http_methods(self) -> Dict:
        return {
            "list": "get",
            "retrieve": "get",
            "create": "post",
            "destroy": "delete",
            "partial_update": "patch",
            "update": "put",
        }

    def view_method_to_http_method(self, view_method_name: str) -> Optional[str]:
        """Maps viewset methods to HTTP methods."""
        return self.view_methods_to_http_methods.get(view_method_name)

    def request(
        self,
        view_method: str,
        force_auth_user: Optional[Any] = None,
        data: Optional[Any] = None,
        content_type: Optional[str] = DEFAULT_CONTENT_TYPE,
        request_factory: Optional[APIRequestFactory] = None,
        basename: str = None,
        url: str = None,
        override_default_storage: bool = False,
        **kwargs,
    ) -> Response:
        """Makes test request and returns response."""
        req_factory = request_factory if request_factory else self.request_factory
        http_method = self.view_method_to_http_method(view_method) or view_method
        view = self._viewset_class.as_view({http_method: view_method}, basename=basename)
        request = getattr(req_factory, http_method)(
            url or self.url,
            data=data,
            content_type=content_type,
            kwargs=kwargs,
        )
        if force_auth_user:
            force_authenticate(request, user=force_auth_user)
        if override_default_storage or self.override_default_storage:
            with override_settings(DEFAULT_FILE_STORAGE=DEFAULT_TEST_STORAGE):
                response = view(request, **kwargs)
        else:
            response = view(request, **kwargs)
        return response.render()
