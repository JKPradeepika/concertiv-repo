from datetime import date
from random import choice, choices
from string import ascii_letters, digits
from typing import Callable, List, Optional

import pytest

from api.models.Buyer import Buyer
from api.models.Employee import Employee
from api.models.Employer import Employer
from api.models.fixtures.person import TypePersonFactory

TypeEmployeeFactory = Callable[..., Employee]


@pytest.fixture
def employee_factory(buyer: Buyer, person_factory: TypePersonFactory) -> TypeEmployeeFactory:
    # Closure
    def create_employee(
        email: str = "aturing@concertiv.com",
        first_name: str = "Alan",
        last_name: str = "Turing",
        phone_number: str = "Turing",
        employer: Employer = buyer.employer,
        hire_date: Optional[date] = None,
        termination_date: Optional[date] = None,
    ) -> Employee:
        person = person_factory(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            employer=employer,
            hire_date=hire_date,
            termination_date=termination_date,
        )

        return Employee.objects.create(person=person)

    return create_employee


@pytest.fixture
def employee(employee_factory: TypeEmployeeFactory) -> Employee:
    return employee_factory(
        email="aturing+{}@concertiv.com".format("".join(choices(ascii_letters + digits, k=choice(range(5, 10)))))
    )


@pytest.fixture
def employees(employee_factory: TypeEmployeeFactory, buyer2: Buyer) -> List[Employee]:
    return [
        employee_factory(email="btbrbng@concertiv.com", first_name="Blbn", last_name="Tbrbng"),
        employee_factory(email="ctcrcng@concertiv.com", first_name="Clcn", last_name="Tcrcng"),
        employee_factory(
            email="dtdrdng@concertiv.com", first_name="Dldn", last_name="Tddcng", employer=buyer2.employer
        ),
        employee_factory(
            email="etereng@concertiv.com", first_name="Elen", last_name="Teeeng", employer=buyer2.employer
        ),
    ]
