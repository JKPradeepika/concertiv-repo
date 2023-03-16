from typing import cast, List, Union

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.urls.resolvers import URLPattern, URLResolver
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from api.routers import constants_router, api_router
from komodo_backend.settings import BASE_URL

schema_view = get_schema_view(
    openapi.Info(
        title="Komodo - APIs Docs",
        default_version="v1.0.0",
        description="REST APIs for Komodo Web Application",
        terms_of_service="https://www.concertiv.com",
        contact=openapi.Contact(email="info@concertiv.com"),
        license=openapi.License(name="BSD Licence"),
    ),
    url=BASE_URL,
    public=True,
    permission_classes=[permissions.AllowAny],
)

schema_view.with_ui("swagger", cache_timeout=0)

base_url_patterns: List[Union[URLPattern, URLResolver]] = [
    # Django Admin
    path("admin/", admin.site.urls),
    # Auth
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # API Docs
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("docs/redoc", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc-ui"),
    # Constants
    path("constants/", include(constants_router.urls)),
    # APIs
    path("", include(api_router.urls)),
]
static_admin_resources: List[Union[URLPattern, URLResolver]] = cast(
    List[Union[URLPattern, URLResolver]],
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
)

urlpatterns = base_url_patterns + static_admin_resources
