from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.utils.translation import gettext_lazy as _

from api.models import (
    AccountContact,
    Address,
    AgreementType,
    AllowedDocumentFileExtension,
    BusinessDeal,
    BusinessType,
    Buyer,
    Contact,
    Contract,
    CoverageGroup,
    CoverageGroupRestriction,
    Department,
    DepartmentRestriction,
    Document,
    DocumentType,
    Employee,
    EmployeeLevel,
    EmployeeLicense,
    Employer,
    EmployerBusinessUnit,
    EmployerCostCenter,
    EmployerCoverageGroup,
    EmployerDepartment,
    EmployerEmployeeLevel,
    EmployerGeography,
    Event,
    Geography,
    GeographyRestriction,
    Industry,
    Person,
    Product,
    ProductType,
    LicensePeriod,
    Subscription,
    SubscriptionPOSGeography,
    Supplier,
    User,
)


@admin.register(AccountContact)
class AccountContactAdmin(admin.ModelAdmin):
    icon_name = "contact_support"
    fields = ("person", "employer", "label", "is_primary", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = ("person", "employer", "label", "is_primary")
    search_fields = ("employer__name", "person__first_name", "person__last_name")
    ordering = ("employer",)


@admin.register(AllowedDocumentFileExtension)
class AllowedDocumentFileExtensionAdmin(admin.ModelAdmin):
    icon_name = "category"
    fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    list_display = ("id", "name", "created_at", "updated_at")
    ordering = ("name", "id")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    icon_name = "location_on"


@admin.register(AgreementType)
class AgreementTypeAdmin(admin.ModelAdmin):
    icon_name = "category"
    fields = (
        "name",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("id", "name", "created_at", "updated_at")
    ordering = ("id",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    icon_name = "contacts"
    fields = (
        "person",
        "description",
        "is_primary",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("person", "description", "is_primary")
    search_fields = (
        "person__email",
        "person__first_name",
        "person__last_name",
        "description",
    )
    ordering = ("person__first_name", "person__last_name", "is_primary")


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    icon_name = "business"
    fields = (
        "name",
        "addresses",
        "industries",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    icon_name = "inventory"
    fields = (
        "resource_action",
        "resource_type",
        "resource_label",
        "resource_json",
        "notes",
        "source_person_label",
        "source_person",
        "employer",
        "domain",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "resource_action",
        "resource_type",
        "resource_label",
        "resource_json",
        "notes",
        "source_person_label",
        "source_person",
        "employer",
        "domain",
        "created_at",
        "updated_at",
    )
    list_display = (
        "source_person_label",
        "resource_action",
        "resource_type",
        "resource_label",
        "employer",
        "notes",
    )
    search_fields = (
        "source_person_label",
        "resource_action",
        "resource_type",
        "resource_label",
        "employer__name",
        "notes",
    )


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    icon_name = "pie_chart"
    fields = (
        "name",
        "domain",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("id", "name", "domain", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("domain",)
    ordering = ("id",)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """Define admin model for our custom Person model with no email field."""

    fields = (
        "email",
        "first_name",
        "last_name",
        "employer",
        "phone_number",
        "job_title",
        "hire_date",
        "termination_date",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = (
        "email",
        "first_name",
        "last_name",
        "employer",
        "phone_number",
        "job_title",
        "hire_date",
        "termination_date",
    )
    search_fields = ("email", "first_name", "last_name", "job_title", "employer__name")
    ordering = ("email", "first_name", "last_name")


class UserCreationForm(BaseUserCreationForm):
    """A custom "Add user" form that skips validation of the password1 and password2 fields"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields["password1"].required = False
        self.fields["password2"].required = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Define admin model for our custom User model with email field."""

    fieldsets = (
        (
            _("Basic information"),
            {"fields": ("person", "email", "password")},
        ),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser", "groups")},
        ),
        (_("Important dates"), {"fields": ("created_at", "updated_at", "last_login")}),
    )
    add_form = UserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "fields": ("person", "email"),
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")
    list_display = ("email", "person", "is_staff", "last_login", "created_at", "updated_at")
    search_fields = ("email", "person__email", "person__first_name", "person__last_name")
    ordering = ("email",)


@admin.register(BusinessDeal)
class BusinessDealAdmin(admin.ModelAdmin):
    icon_name = "compare_arrows"
    fields = ("buyer", "supplier", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = ("buyer", "supplier", "created_at", "updated_at")
    search_fields = ("buyer__employer__name", "supplier__employer__name")
    ordering = ("buyer__employer__name", "supplier__employer__name")


@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    icon_name = "category"
    fields = (
        "name",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("id", "name", "created_at", "updated_at")
    ordering = ("id",)


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    icon_name = "business"
    fields = (
        "employer",
        "short_name",
        "short_code",
        "account_status",
        "savings_report_frequency_in_months",
        "industries",
        "geographies",
        "first_joined_at",
        "termination_date",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = (
        "employer",
        "short_name",
        "short_code",
        "account_status",
        "savings_report_frequency_in_months",
        "first_joined_at",
        "termination_date",
    )
    search_fields = ("employer__name", "short_name", "short_code")
    ordering = ("employer__name",)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    icon_name = "file_copy"
    fields = (
        "business_deal",
        "buyer_entity_name",
        "status",
        "signed_date",
        "start_date",
        "end_date",
        "autorenewal_duration",
        "autorenewal_duration_unit",
        "autorenewal_deadline",
        "terminated_at",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = (
        "business_deal",
        "buyer_entity_name",
        "status",
        "signed_date",
        "start_date",
        "end_date",
        "autorenewal_duration",
        "autorenewal_duration_unit",
        "autorenewal_deadline",
        "terminated_at",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "buyer_entity_name",
        "business_deal__buyer__employer__name",
        "business_deal__supplier__employer__name",
    )
    ordering = ("buyer_entity_name", "start_date")


@admin.register(EmployerCostCenter)
class EmployerCostCenterAdmin(admin.ModelAdmin):
    icon_name = "pie_chart"
    fields = ("name", "employer", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = ("name", "employer", "created_at", "updated_at")
    search_fields = ("name", "employer__name")
    ordering = ("employer__name", "name")


@admin.register(CoverageGroup)
class CoverageGroupAdmin(admin.ModelAdmin):
    icon_name = "pie_chart"
    fields = (
        "name",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("id",)


@admin.register(CoverageGroupRestriction)
class CoverageGroupRestrictionAdmin(admin.ModelAdmin):
    icon_name = "phonelink_lock"
    fields = ("subscription", "employer_coverage_group", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = ("subscription", "employer_coverage_group", "created_at", "updated_at")
    search_fields = (
        "subscription__name",
        "employer_coverage_group__name",
        "employer_coverage_group__coverage_group__name",
    )
    ordering = ("subscription", "employer_coverage_group")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    icon_name = "pie_chart"
    fields = (
        "name",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("id",)


@admin.register(DepartmentRestriction)
class DepartmentRestrictionAdmin(admin.ModelAdmin):
    icon_name = "phonelink_lock"
    fields = ("subscription", "employer_department", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = ("subscription", "employer_department", "created_at", "updated_at")
    search_fields = (
        "subscription__name",
        "employer_department__name",
        "employer_department__department__name",
    )
    ordering = ("subscription", "employer_department")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    icon_name = "pie_chart"
    fields = (
        "name",
        "type",
        "date",
        "file",
        "notes",
        "buyer",
        "supplier",
        "contract",
        "product",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("date", "created_at", "updated_at")
    list_display = (
        "id",
        "name",
        "type",
        "date",
        "file",
        "notes",
        "buyer",
        "supplier",
        "contract",
        "product",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
    list_filter = ("type", "buyer", "supplier", "contract", "product")
    ordering = ("id",)


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    icon_name = "compare_arrows"
    fields = (
        "name",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("id",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Define admin model for our custom Employee model with no email field."""

    fields = (
        "person",
        "employer_cost_center",
        "employer_employee_level",
        "employer_coverage_group",
        "employer_department",
        "employer_geography",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = (
        "person",
        "employer_cost_center",
        "employer_employee_level",
        "employer_coverage_group",
        "employer_department",
        "employer_geography",
    )
    search_fields = ("person__email", "person__first_name", "person__last_name")
    ordering = ("person__email", "person__first_name", "person__last_name")


@admin.register(EmployeeLevel)
class EmployeeLevelAdmin(admin.ModelAdmin):
    icon_name = "pie_chart"
    fields = (
        "name",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("id",)


@admin.register(EmployeeLicense)
class EmployeeLicenseAdmin(admin.ModelAdmin):
    icon_name = "pie_chart"
    fields = ("employee", "subscription", "start_date", "end_date", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = ("employee", "subscription", "start_date", "end_date", "created_at", "updated_at")
    search_fields = ("employee__person__first_name", "employee__person__last_name", "subscription__name")
    ordering = ("employee", "subscription", "start_date")


@admin.register(EmployerBusinessUnit)
class EmployerBusinessUnitAdmin(admin.ModelAdmin):
    icon_name = "compare_arrows"
    fields = ("employer", "name", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = ("employer", "name", "created_at", "updated_at")
    search_fields = ("employer", "name")
    ordering = ("employer", "name")


@admin.register(EmployerCoverageGroup)
class EmployerCoverageGroupAdmin(admin.ModelAdmin):
    icon_name = "pie_chart"
    fields = ("employer", "coverage_group", "name", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = ("employer", "coverage_group", "name", "created_at", "updated_at")
    search_fields = ("employer__name", "name", "coverage_group__name")
    ordering = ("employer__name", "name", "coverage_group__name")


@admin.register(EmployerDepartment)
class EmployerDepartmentAdmin(admin.ModelAdmin):
    icon_name = "pie_chart"
    fields = ("employer", "department", "name", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = ("employer", "department", "name", "created_at", "updated_at")
    search_fields = ("employer__name", "name", "department__name")
    ordering = ("employer__name", "name", "department__name")


@admin.register(EmployerEmployeeLevel)
class EmployerEmployeeLevelAdmin(admin.ModelAdmin):
    icon_name = "pie_chart"
    fields = ("employer", "employee_level", "name", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = ("employer", "employee_level", "name", "created_at", "updated_at")
    search_fields = ("employer__name", "name", "employee_level__name")
    ordering = ("employer__name", "name", "employee_level__name")


@admin.register(EmployerGeography)
class EmployerGeographyAdmin(admin.ModelAdmin):
    icon_name = "map"
    fields = ("employer", "geography", "parent", "name", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = ("employer", "geography", "parent", "name", "created_at", "updated_at")
    search_fields = ("employer__name", "parent__name", "name", "geography__name")
    ordering = ("employer__name", "parent__name", "name", "geography__name")


@admin.register(Geography)
class GeographyAdmin(admin.ModelAdmin):
    icon_name = "map"
    fields = (
        "name",
        "domain",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("id", "name", "created_at", "updated_at")
    ordering = ("id",)


@admin.register(GeographyRestriction)
class GeographyRestrictionAdmin(admin.ModelAdmin):
    icon_name = "vpn_lock"
    fields = ("subscription", "employer_geography", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = ("subscription", "employer_geography", "created_at", "updated_at")
    search_fields = (
        "subscription__name",
        "employer_geography__name",
        "employer_geography__parent__name",
        "employer_geography__parent__geography__name",
        "employer_geography__geography__name",
    )
    ordering = ("subscription", "employer_geography")


@admin.register(SubscriptionPOSGeography)
class SubscriptionPOSGeographyAdmin(admin.ModelAdmin):
    icon_name = "map"
    fields = (
        "created_at",
        "updated_at",
        "geography",
        "subscription",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("id", "geography", "subscription", "created_at", "updated_at")
    search_fields = ("geography__name", "subscription__name")
    ordering = ("id",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    icon_name = "category"
    fields = (
        "name",
        "supplier",
        "description",
        "contacts",
        "types",
        "industries",
        "geographies",
        "domain",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("name", "supplier", "domain", "created_at", "updated_at")
    search_fields = ("name", "supplier__employer__name", "description")
    ordering = ("name", "supplier")


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    icon_name = "pie_chart"
    fields = (
        "name",
        "domain",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("id", "name", "domain", "created_at", "updated_at")
    list_filter = ("domain",)
    ordering = ("id",)


@admin.register(LicensePeriod)
class LicensePeriodAdmin(admin.ModelAdmin):
    icon_name = "attach_money"
    fields = (
        "subscription",
        "type",
        "price",
        "exchange_rate_to_usd_at_time_of_purchase",
        "start_date",
        "end_date",
        "max_credits",
        "max_users",
        "incremental_user_price",
        "usage_unit_price",
        "usage_unit",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = (
        "subscription",
        "type",
        "price",
        "start_date",
        "end_date",
        "max_credits",
        "max_users",
        "incremental_user_price",
        "usage_unit_price",
        "usage_unit",
        "exchange_rate_to_usd_at_time_of_purchase",
    )
    search_fields = (
        "subscription__name",
        "subscription__product__name",
        "type",
        "usage_unit",
    )
    ordering = ("subscription",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    icon_name = "compare_arrows"
    fields = (
        "notes",
        "contract",
        "product",
        "contacts",
        "name",
        "created_at",
        "updated_at",
        "billing_frequency",
        "tax_rate",
    )
    readonly_fields = ["created_at", "updated_at"]
    list_display = ("name", "contract", "product", "created_at", "updated_at", "billing_frequency", "tax_rate")
    search_fields = ("product__name", "name", "notes")
    ordering = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    icon_name = "location_city"
    fields = ("employer", "description", "url", "type", "is_nda_signed", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = (
        "employer",
        "description",
        "url",
        "type",
        "is_nda_signed",
    )
    search_fields = ("employer__name", "is_nda_signed", "description")
    ordering = ("employer__name",)
