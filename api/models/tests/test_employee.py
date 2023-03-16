from datetime import date, timedelta

import pytest

from api.constants import (
    EMPLOYMENT_STATUS_ACTIVE,
    EMPLOYMENT_STATUS_INACTIVE,
    EMPLOYMENT_STATUS_UPCOMING_DEPARTURE,
    EMPLOYMENT_STATUS_UPCOMING_HIRE,
)
from api.models.fixtures import TypeEmployeeFactory


today = date.today()
tomorrow = today + timedelta(days=1)
long_time_from_now = today + timedelta(weeks=20)
yesterday = today - timedelta(days=1)
long_time_ago = today - timedelta(weeks=100)

employee_email_1 = "btbrbng@concertiv.com"
employee_email_2 = "ctbrbng@concertiv.com"
employee_email_3 = "dtbrbng@concertiv.com"
employee_email_4 = "etbrbng@concertiv.com"


@pytest.mark.django_db
def test_employee_status_calculation_default(
    employee_factory: TypeEmployeeFactory,
) -> None:
    employee = employee_factory(email=employee_email_1)
    assert employee.employment_status == EMPLOYMENT_STATUS_ACTIVE


@pytest.mark.django_db
def test_employee_status_calculation_hire_date_past(
    employee_factory: TypeEmployeeFactory,
) -> None:

    employee1 = employee_factory(email=employee_email_1, hire_date=yesterday)
    employee2 = employee_factory(email=employee_email_2, hire_date=long_time_ago)
    assert employee1.employment_status == EMPLOYMENT_STATUS_ACTIVE
    assert employee2.employment_status == EMPLOYMENT_STATUS_ACTIVE


@pytest.mark.django_db
def test_employee_status_calculation_hire_date_today(
    employee_factory: TypeEmployeeFactory,
) -> None:
    employee = employee_factory(email=employee_email_1, hire_date=today)
    assert employee.employment_status == EMPLOYMENT_STATUS_ACTIVE


@pytest.mark.django_db
def test_employee_status_calculation_hire_date_future(
    employee_factory: TypeEmployeeFactory,
) -> None:
    employee1 = employee_factory(email=employee_email_1, hire_date=tomorrow)
    employee2 = employee_factory(email=employee_email_2, hire_date=long_time_from_now)
    assert employee1.employment_status == EMPLOYMENT_STATUS_UPCOMING_HIRE
    assert employee2.employment_status == EMPLOYMENT_STATUS_UPCOMING_HIRE


@pytest.mark.django_db
def test_employee_status_calculation_termination_date_today(
    employee_factory: TypeEmployeeFactory,
) -> None:
    employee = employee_factory(email=employee_email_1, termination_date=today)
    assert employee.employment_status == EMPLOYMENT_STATUS_INACTIVE


@pytest.mark.django_db
def test_employee_status_calculation_termination_date_past(
    employee_factory: TypeEmployeeFactory,
) -> None:
    employee1 = employee_factory(email=employee_email_1, termination_date=yesterday)
    employee2 = employee_factory(email=employee_email_2, termination_date=long_time_ago)
    assert employee1.employment_status == EMPLOYMENT_STATUS_INACTIVE
    assert employee2.employment_status == EMPLOYMENT_STATUS_INACTIVE


@pytest.mark.django_db
def test_employee_status_calculation_termination_date_future(
    employee_factory: TypeEmployeeFactory,
) -> None:
    employee1 = employee_factory(email=employee_email_1, termination_date=tomorrow)
    employee2 = employee_factory(email=employee_email_2, termination_date=long_time_from_now)
    assert employee1.employment_status == EMPLOYMENT_STATUS_UPCOMING_DEPARTURE
    assert employee2.employment_status == EMPLOYMENT_STATUS_UPCOMING_DEPARTURE


@pytest.mark.django_db
def test_employee_status_calculation_hire_and_termination_date_today(
    employee_factory: TypeEmployeeFactory,
) -> None:
    employee = employee_factory(email=employee_email_1, hire_date=today, termination_date=today)
    assert employee.employment_status == EMPLOYMENT_STATUS_INACTIVE


@pytest.mark.django_db
def test_employee_status_calculation_hire_and_termination_date_past(
    employee_factory: TypeEmployeeFactory,
) -> None:
    employee1 = employee_factory(
        email=employee_email_1,
        hire_date=yesterday,
        termination_date=yesterday,
    )
    employee2 = employee_factory(
        email=employee_email_2,
        hire_date=long_time_ago,
        termination_date=yesterday,
    )
    employee3 = employee_factory(
        email=employee_email_3,
        hire_date=yesterday,
        termination_date=long_time_ago,
    )
    employee4 = employee_factory(
        email=employee_email_4,
        hire_date=long_time_ago,
        termination_date=long_time_ago,
    )
    assert employee1.employment_status == EMPLOYMENT_STATUS_INACTIVE
    assert employee2.employment_status == EMPLOYMENT_STATUS_INACTIVE
    assert employee3.employment_status == EMPLOYMENT_STATUS_INACTIVE
    assert employee4.employment_status == EMPLOYMENT_STATUS_INACTIVE


@pytest.mark.django_db
def test_employee_status_calculation_hire_and_termination_date_future(
    employee_factory: TypeEmployeeFactory,
) -> None:
    employee1 = employee_factory(email=employee_email_1, hire_date=tomorrow, termination_date=tomorrow)
    employee2 = employee_factory(email=employee_email_2, hire_date=tomorrow, termination_date=long_time_from_now)
    employee3 = employee_factory(email=employee_email_3, hire_date=long_time_from_now, termination_date=tomorrow)
    employee4 = employee_factory(
        email=employee_email_4, hire_date=long_time_from_now, termination_date=long_time_from_now
    )
    assert employee1.employment_status == EMPLOYMENT_STATUS_UPCOMING_DEPARTURE
    assert employee2.employment_status == EMPLOYMENT_STATUS_UPCOMING_DEPARTURE
    assert employee3.employment_status == EMPLOYMENT_STATUS_UPCOMING_DEPARTURE
    assert employee4.employment_status == EMPLOYMENT_STATUS_UPCOMING_DEPARTURE
