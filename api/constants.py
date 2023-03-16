"""
    Constants
    variables and values that will be used in whatever place in the code
"""
from django.utils.translation import gettext_lazy as _

MAX_FILE_BYTES = 25 * 1024 * 1024  # 25 MB
MAX_FILE_SIZE_PRETTY_NAME = "25 MB"

# Domains
DOMAIN_MARKET_DATA = 1
DOMAIN_TECHNOLOGY = 2
DOMAIN_TRAVEL = 3
DOMAIN_INSURANCE = 4
DOMAINS = (
    (DOMAIN_MARKET_DATA, _("Market Data")),
    (DOMAIN_TECHNOLOGY, _("Technology")),
    (DOMAIN_TRAVEL, _("Travel")),
    (DOMAIN_INSURANCE, _("Insurance")),
)

# Contact Labels
CONTACT_LABEL_INVOICE_RECIPIENT = 1
CONTACT_LABEL_LEGAL = 2
CONTACT_LABEL_MEMBERSHIP_UPDATE = 3
CONTACT_LABEL_RENEWAL_UPDATE = 4
CONTACT_LABEL_SUBSCRIPTION_NOTIFICATION = 5
CONTACT_LABELS = (
    (CONTACT_LABEL_INVOICE_RECIPIENT, _("Invoice Recipient")),
    (CONTACT_LABEL_LEGAL, _("Legal")),
    (CONTACT_LABEL_MEMBERSHIP_UPDATE, _("Membership Update")),
    (CONTACT_LABEL_RENEWAL_UPDATE, _("Renewal Update")),
    (CONTACT_LABEL_SUBSCRIPTION_NOTIFICATION, _("Subscription Notification")),
)

# Contact Types
CONTACT_TYPE_BUYER_CONTACT = 1
CONTACT_TYPE_SUPPLIER_CONTACT = 2
CONTACT_TYPE_PRODUCT_CONTACT = 3
CONTACT_TYPES = (
    (CONTACT_TYPE_BUYER_CONTACT, _("Buyer Contact")),
    (CONTACT_TYPE_SUPPLIER_CONTACT, _("Supplier Contact")),
    (CONTACT_TYPE_PRODUCT_CONTACT, _("Product Contact")),
)

# Account Contact Label
ACCOUNT_CONTACT_LABEL_AM_400_MARKET_DATA = 1
ACCOUNT_CONTACT_LABEL_AM_400_TECHNOLOGY = 2
ACCOUNT_CONTACT_LABEL_AM_400_TRAVEL = 3
ACCOUNT_CONTACT_LABEL_AM_400_INSURANCE = 4
ACCOUNT_CONTACT_LABEL_AM_200_SENIOR = 5
ACCOUNT_CONTACT_LABEL_OTHER = 6
ACCOUNT_CONTACT_LABELS = (
    (ACCOUNT_CONTACT_LABEL_AM_400_MARKET_DATA, _("Market Data Contact")),
    (ACCOUNT_CONTACT_LABEL_AM_400_TECHNOLOGY, _("Technology Contact")),
    (ACCOUNT_CONTACT_LABEL_AM_400_TRAVEL, _("Travel Contact")),
    (ACCOUNT_CONTACT_LABEL_AM_400_INSURANCE, _("Insurance Contact")),
    (ACCOUNT_CONTACT_LABEL_AM_200_SENIOR, _("Senior Account Contact")),
    (ACCOUNT_CONTACT_LABEL_OTHER, _("Other")),
)

# Statuses
STATUS_ACTIVE = 1
STATUS_EXPIRED = 2
STATUS_TERMINATED = 3
STATUSES = (
    (STATUS_ACTIVE, _("Active")),
    (STATUS_EXPIRED, _("Expired")),
    (STATUS_TERMINATED, _("Terminated")),
)

# Resource Actions
RESOURCE_ACTION_ADD = 1
RESOURCE_ACTION_CHANGE = 2
RESOURCE_ACTION_TERMINATE = 3
RESOURCE_ACTION_REMOVE = 4
RESOURCE_ACTION_ACTIVATE = 5
RESOURCES_ACTIONS = (
    (RESOURCE_ACTION_ADD, _("Add")),
    (RESOURCE_ACTION_CHANGE, _("Change")),
    (RESOURCE_ACTION_TERMINATE, _("Terminate")),
    (RESOURCE_ACTION_REMOVE, _("Remove")),
    (RESOURCE_ACTION_ACTIVATE, _("Activate")),
)

# Resource Types
RESOURCE_TYPE_SUBSCRIPTION = 1
RESOURCE_TYPE_LICENSE = 2
RESOURCE_TYPE_USER = 3
RESOURCES_TYPES = (
    (RESOURCE_TYPE_SUBSCRIPTION, _("Subscription")),
    (RESOURCE_TYPE_LICENSE, _("License")),
    (RESOURCE_TYPE_USER, _("User")),
)

# Product Statuses
PRODUCT_STATUS_ACTIVE = 1
PRODUCT_STATUS_INACTIVE = 2
PRODUCT_STATUS_LEGACY = 3
PRODUCT_STATUSES = (
    (PRODUCT_STATUS_ACTIVE, _("Active")),
    (PRODUCT_STATUS_INACTIVE, _("Inactive")),
    (PRODUCT_STATUS_LEGACY, _("Legacy")),
)

# Employment Statuses
EMPLOYMENT_STATUS_ACTIVE = 1
EMPLOYMENT_STATUS_INACTIVE = 2
EMPLOYMENT_STATUS_UPCOMING_HIRE = 3
EMPLOYMENT_STATUS_UPCOMING_DEPARTURE = 4
EMPLOYMENT_STATUSES = (
    (EMPLOYMENT_STATUS_ACTIVE, _("Active")),
    (EMPLOYMENT_STATUS_INACTIVE, _("Inactive")),
    (EMPLOYMENT_STATUS_UPCOMING_HIRE, _("Upcoming Hire")),
    (EMPLOYMENT_STATUS_UPCOMING_DEPARTURE, _("Upcoming Departure")),
)


# Licenses Periods Statuses
LICENSE_PERIOD_STATUS_ACTIVE = 1
LICENSE_PERIOD_STATUS_INACTIVE = 2
LICENSE_PERIOD_STATUS_UPCOMING = 3
LICENSES_PERIODS_STATUSES = (
    (LICENSE_PERIOD_STATUS_ACTIVE, _("Active")),
    (LICENSE_PERIOD_STATUS_INACTIVE, _("Inactive")),
    (LICENSE_PERIOD_STATUS_UPCOMING, _("Upcoming")),
)

# Licenses Periods Types
LICENSE_PERIOD_TYPE_ENTERPRISE = 1
LICENSE_PERIOD_TYPE_USER_LIMIT = 2
LICENSE_PERIOD_TYPE_PER_USER = 3
LICENSE_PERIOD_TYPE_PREPAID_CREDIT = 4
LICENSE_PERIOD_TYPE_USAGE_BASED = 5
LICENSE_PERIOD_TYPE_OTHER = 6
LICENSES_PERIODS_TYPES = (
    (LICENSE_PERIOD_TYPE_ENTERPRISE, _("Enterprise")),
    (LICENSE_PERIOD_TYPE_USER_LIMIT, _("User Limit")),
    (LICENSE_PERIOD_TYPE_PER_USER, _("Per User")),
    (LICENSE_PERIOD_TYPE_PREPAID_CREDIT, _("Prepaid Credit")),
    (LICENSE_PERIOD_TYPE_USAGE_BASED, _("Usage Based")),
    (LICENSE_PERIOD_TYPE_OTHER, _("Other")),
)

# Licenses Periods Types Requirements
LICENSE_PERIODS_TYPES_REQUIREMENTS = {
    LICENSE_PERIOD_TYPE_ENTERPRISE: {
        "required": [],
        "invisible": [
            "maxUsers",
            "maxCredits",
            "incrementalUserPrice",
            "incrementalUserPriceCurrency",
        ],
    },
    LICENSE_PERIOD_TYPE_USER_LIMIT: {
        "required": ["maxUsers"],
        "invisible": ["maxCredits"],
    },
    LICENSE_PERIOD_TYPE_PER_USER: {
        "required": [],
        "invisible": ["maxCredits"],
    },
    LICENSE_PERIOD_TYPE_PREPAID_CREDIT: {
        "required": ["maxCredits"],
        "invisible": ["maxUsers"],
    },
    LICENSE_PERIOD_TYPE_USAGE_BASED: {
        "required": [],
        "invisible": [],
    },
    LICENSE_PERIOD_TYPE_OTHER: {
        "required": [],
        "invisible": [
            "maxUsers",
            "maxCredits",
            "incrementalUserPrice",
            "incrementalUserPriceCurrency",
        ],
    },
}

# Licenses Periods Usages Units
LICENSE_PERIOD_USAGE_UNIT_CREDIT = 1
LICENSE_PERIOD_USAGE_UNIT_REPORT = 2
LICENSE_PERIOD_USAGE_UNIT_GB = 3
LICENSE_PERIOD_USAGE_UNIT_TB = 4
LICENSE_PERIOD_USAGE_UNIT_CIRCUIT = 5
LICENSE_PERIOD_USAGE_UNIT_DEVICE = 6
LICENSE_PERIOD_USAGE_UNIT_OTHER = 7
LICENSES_PERIODS_USAGE_UNITS = (
    (LICENSE_PERIOD_USAGE_UNIT_CREDIT, _("Credit")),
    (LICENSE_PERIOD_USAGE_UNIT_REPORT, _("Report")),
    (LICENSE_PERIOD_USAGE_UNIT_GB, _("Gb")),
    (LICENSE_PERIOD_USAGE_UNIT_TB, _("Tb")),
    (LICENSE_PERIOD_USAGE_UNIT_CIRCUIT, _("Circuit")),
    (LICENSE_PERIOD_USAGE_UNIT_DEVICE, _("Device")),
    (LICENSE_PERIOD_USAGE_UNIT_OTHER, _("Other")),
)

# Buyer Statuses
BUYER_STATUS_ACTIVE = 1
BUYER_STATUS_INACTIVE = 2
BUYER_STATUSES = (
    (BUYER_STATUS_ACTIVE, _("Active")),
    (BUYER_STATUS_INACTIVE, _("Inactive")),
)

# Contract Duration Units
CONTRACT_DURATION_UNIT_DAYS = 1  # removed
CONTRACT_DURATION_UNIT_WEEKS = 2  # removed
CONTRACT_DURATION_UNIT_MONTHS = 3
CONTRACT_DURATION_UNIT_YEARS = 4
CONTRACT_DURATION_UNITS = (
    (CONTRACT_DURATION_UNIT_MONTHS, _("Month(s)")),
    (CONTRACT_DURATION_UNIT_YEARS, _("Year(s)")),
)

# Contract Statuses
CONTRACT_STATUS_ACTIVE = 1
CONTRACT_STATUS_UPCOMING = 2
CONTRACT_STATUS_EXPIRED = 3
CONTRACT_STATUS_TERMINATED = 4
CONTRACT_STATUSES = (
    (CONTRACT_STATUS_ACTIVE, _("Active")),
    (CONTRACT_STATUS_UPCOMING, _("Upcoming")),
    (CONTRACT_STATUS_EXPIRED, _("Expired")),
    (CONTRACT_STATUS_TERMINATED, _("Terminated")),
)


# Subscription Billing Frequency
SUBSCRIPTION_BILLING_FREQUENCY_ONCE = 1
SUBSCRIPTION_BILLING_FREQUENCY_MONTHLY = 2
SUBSCRIPTION_BILLING_FREQUENCY_QUARTERLY = 3
SUBSCRIPTION_BILLING_FREQUENCY_SEMIANNUALLY = 4
SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY = 5
SUBSCRIPTION_BILLING_FREQUENCIES = (
    (SUBSCRIPTION_BILLING_FREQUENCY_ONCE, _("Once")),
    (SUBSCRIPTION_BILLING_FREQUENCY_MONTHLY, _("Monthly")),
    (SUBSCRIPTION_BILLING_FREQUENCY_QUARTERLY, _("Quarterly")),
    (SUBSCRIPTION_BILLING_FREQUENCY_SEMIANNUALLY, _("Semiannually")),
    (SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY, _("Annually")),
)

# Travel Domain Discount Types
DISCOUNT_TYPE_FIXED = 1
DISCOUNT_TYPE_PERCENTAGE = 2
DISCOUNT_TYPES = (
    (DISCOUNT_TYPE_FIXED, _("Fixed")),
    (DISCOUNT_TYPE_PERCENTAGE, _("Percentage")),
)

# Supplier Types
SUPPLIER_TYPE_GENERAL = 1
SUPPLIER_TYPE_TMC = 2
SUPPLIER_TYPE_RESELLER = 3
SUPPLIER_TYPES = (
    (SUPPLIER_TYPE_GENERAL, _("General")),
    (SUPPLIER_TYPE_TMC, _("TMC")),
    (SUPPLIER_TYPE_RESELLER, _("Reseller")),
)

# Ignored contract fields by domain
IGNORED_CONTRACT_FIELDS_BY_DOMAIN = {
    DOMAIN_MARKET_DATA: {
        "contract": [],
        "auto_renewal": [],
        "subscription": [
            "resellerSupplier",
            "resellerSupplierId",
            "tmcSupplier",
            "tmcSupplierId",
            "discountType",
            "posGeographies",
            "posGeographyIds",
        ],
        "license_period": [],
    },
    DOMAIN_TECHNOLOGY: {
        "contract": [],
        "auto_renewal": [],
        "subscription": [
            "posGeographies",
            "posGeographyIds",
            "tmcSupplier",
            "tmcSupplierId",
            "discountType",
        ],
        "license_period": [],
    },
    DOMAIN_TRAVEL: {
        "contract": [],
        "auto_renewal": [],
        "subscription": [
            "restrictions.employerGeographyIds",
            "restrictions.employerDepartmentIds",
            "restrictions.employerCoverageGroupIds",
            "geographyRestrictions",
            "departmentRestrictions",
            "coverageGroupRestrictions",
            "resellerSupplier",
            "resellerSupplierId",
            "activeEmployeeLicenseCount",
            "calculatedTotalPricePerUser",
        ],
        "license_period": [
            "incrementalUserPrice",
            "incrementalUserPriceCurrency",
            "maxCredits",
            "maxUsers",
            "usageUnit",
            "usageUnitPrice",
            "usageUnitPriceCurrency",
        ],
    },
    DOMAIN_INSURANCE: {
        "contract": [],
        "auto_renewal": [],
        "subscription": [],
        "license_period": [],
    },
}


# # # # # CONSTANTS OBJECTS (for dynamic routing in endpoints) # # # # #
CONSTANTS_OBJECTS = {
    "domains": DOMAINS,
    "contacts-labels": CONTACT_LABELS,
    "contacts-types": CONTACT_TYPES,
    "accounts-contacts-labels": ACCOUNT_CONTACT_LABELS,
    "statuses": STATUSES,
    "resources-actions": RESOURCES_ACTIONS,
    "resources-types": RESOURCES_TYPES,
    "products-statuses": PRODUCT_STATUSES,
    "employments-statuses": EMPLOYMENT_STATUSES,
    "licenses-periods-statuses": LICENSES_PERIODS_STATUSES,
    "licenses-periods-types": LICENSES_PERIODS_TYPES,
    "licenses-periods-types-requirements": LICENSE_PERIODS_TYPES_REQUIREMENTS,
    "licenses-periods-usages-units": LICENSES_PERIODS_USAGE_UNITS,
    "buyers-statuses": BUYER_STATUSES,
    "contracts-durations-units": CONTRACT_DURATION_UNITS,
    "contracts-statuses": CONTRACT_STATUSES,
    "subscriptions-billings-frequencies": SUBSCRIPTION_BILLING_FREQUENCIES,
    "discount-types": DISCOUNT_TYPES,
    "supplier-types": SUPPLIER_TYPES,
    "ignored-contract-fields-by-domain": IGNORED_CONTRACT_FIELDS_BY_DOMAIN,
}
