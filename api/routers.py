from rest_framework import routers

from api.constants import CONSTANTS_OBJECTS
from api.viewsets import (
    AgreementTypeViewSet,
    BuyerViewSet,
    BusinessTypeViewSet,
    ConstantViewSet,
    ContractViewSet,
    ContractSeriesViewSet,
    DocumentViewSet,
    EmployeeViewSet,
    EmployerBusinessUnitViewSet,
    EmployerCostCenterViewSet,
    EmployerCoverageGroupViewSet,
    EmployerDepartmentViewSet,
    EmployerEmployeeLevelViewSet,
    EmployerGeographyViewSet,
    EmployeeLicenseViewSet,
    GeographyViewSet,
    IndustryViewSet,
    LicensePeriodViewSet,
    ProductTypeViewSet,
    ProductViewSet,
    SubscriptionViewSet,
    SupplierViewSet,
    UserViewSet,
)
from api.viewsets.ForgotPasswordViewSet import ForgotPasswordViewSet

# # # API router
api_router = routers.DefaultRouter(trailing_slash=False)

api_router.register(r"agreements-types", AgreementTypeViewSet, basename="agreements-types")
api_router.register(r"business-units", EmployerBusinessUnitViewSet, basename="business-units")
api_router.register(r"business-types", BusinessTypeViewSet, basename="business-types")
api_router.register(r"buyers", BuyerViewSet, basename="buyers")
api_router.register(r"contracts", ContractViewSet, basename="contracts")
api_router.register(r"contract-series", ContractSeriesViewSet, basename="contract-series")
api_router.register(r"documents", DocumentViewSet, basename="documents")
api_router.register(r"subscriptions", SubscriptionViewSet, basename="subscriptions")
api_router.register(r"cost-centers", EmployerCostCenterViewSet, basename="cost-centers")
api_router.register(r"coverage-groups", EmployerCoverageGroupViewSet, basename="coverage-groups")
api_router.register(r"departments", EmployerDepartmentViewSet, basename="departments")
api_router.register(r"employee-levels", EmployerEmployeeLevelViewSet, basename="employee-levels")
api_router.register(r"employees", EmployeeViewSet, basename="employees")
api_router.register(r"employees-licenses", EmployeeLicenseViewSet, basename="employees-licenses")
api_router.register(r"employer-geographies", EmployerGeographyViewSet, basename="employer-geographies")
api_router.register(r"geographies", GeographyViewSet, basename="geographies")
api_router.register(r"industries", IndustryViewSet, basename="industries")
api_router.register(r"product-types", ProductTypeViewSet, basename="product-types")
api_router.register(r"products", ProductViewSet, basename="products")
api_router.register(r"licenses-periods", LicensePeriodViewSet, basename="licenses-periods")
api_router.register(r"suppliers", SupplierViewSet, basename="suppliers")
api_router.register(r"users", UserViewSet, basename="users")
api_router.register(r"forgot-password", ForgotPasswordViewSet, basename="forgot-password")

# Constants router
constants_router = routers.SimpleRouter(trailing_slash=False)

# dynamic way to create endpoints for constants based on basename
for key, value in CONSTANTS_OBJECTS.items():
    constants_router.register(r"%s" % key, ConstantViewSet, basename=key)
