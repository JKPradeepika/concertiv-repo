import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    "model_fixture_name",
    [
        "account_contact",
        "address",
        "business_deal",
        "buyer",
        "contact",
        "contract",
        "coverage_group",
        "coverage_group_restriction",
        "department",
        "department_restriction",
        "document",
        "document_type",
        "employee",
        "employee_level",
        "employer",
        "employer_business_unit",
        "employer_cost_center",
        "employer_coverage_group",
        "employer_department",
        "employer_employee_level",
        "employer_geography",
        "event",
        "geography",
        "geography_restriction",
        "industry",
        "person",
        "product",
        "product_type",
        "license_period",
        "subscription",
        "supplier",
        "user",
    ],
)
def test__str__executes_without_crashing(model_fixture_name: str, request: pytest.FixtureRequest) -> None:
    model_instance = request.getfixturevalue(model_fixture_name)
    model_instance.__str__()
