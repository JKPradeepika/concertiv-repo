import json
from typing import Dict, Optional

import pytest
from rest_framework import status
from rest_framework.serializers import ErrorDetail

from api.models import Buyer, Employee, User
from api.models.fixtures import TypeBuyerFactory, TypeEmployeeFactory
from api.viewsets.EmployeeViewSet import EmployeeViewSet, column_name_mappings
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource

employees_test_resource = ViewSetTestResource(EmployeeViewSet, "employees-list")


class TestGetEmployee:
    @pytest.mark.django_db
    def test_get_employees_can_list_employees(
        self,
        buyer_factory: TypeBuyerFactory,
        employee_factory: TypeEmployeeFactory,
        user: User,
    ) -> None:
        """Test that we can list employees"""
        another_buyer = buyer_factory(name="Yet Another Company Name", short_name="YACN", short_code="YACN")
        employees = [
            employee_factory(email="btbrbng@concertiv.com", first_name="Blbn", last_name="Tbrbng"),
            employee_factory(email="ctcrcng@concertiv.com", first_name="Clcn", last_name="Tcrcng"),
            employee_factory(
                email="etereng@concertiv.com", first_name="Flfn", last_name="Teeeng", employer=another_buyer.employer
            ),
        ]

        response = employees_test_resource.request("list", user)

        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(employees)

    @pytest.mark.django_db
    def test_get_employees_can_list_employees_filtered_by_buyer_id(
        self,
        buyer_factory: TypeBuyerFactory,
        employee_factory: TypeEmployeeFactory,
        user: User,
    ) -> None:
        """Test that we can list employees filtered by buyer id"""
        another_buyer = buyer_factory(name="Yet Another Company Name", short_name="YACN", short_code="YACN")
        employees = [
            employee_factory(email="btbrbng@concertiv.com", first_name="rlrn", last_name="Tbrbng"),
            employee_factory(
                email="dtdrdng@concertiv.com", first_name="Dldn", last_name="Tddcng", employer=another_buyer.employer
            ),
            employee_factory(
                email="etereng@concertiv.com", first_name="Elen", last_name="Teeeng", employer=another_buyer.employer
            ),
        ]
        response = employees_test_resource.request(
            "list", user, data={"buyerId": employees[0].person.employer.buyer.id}
        )
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(
            Employee.objects.filter(person__employer__buyer__id=employees[0].person.employer.buyer.id)
        )
        for employee in response.data["results"]:
            assert employee["buyerId"] == employees[0].person.employer.buyer.id

    @pytest.mark.django_db
    def test_get_employees_can_fetch_employee_by_id(self, employee: Employee, user: User) -> None:
        """Test that we can fetch a employee by ID"""
        response = employees_test_resource.request("retrieve", user, pk=employee.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employee.id


@pytest.mark.parametrize(
    "filter_column",
    column_name_mappings.keys(),
)
@pytest.mark.django_db
class TestListEmployeeFilterColumns:
    def test_column_mappings_valid(self, user: User, filter_column: str, employee: Employee) -> None:
        response = employees_test_resource.request(
            "list", user, data={"filterContent": f"{filter_column} equals '1'", "filterOperator": "and"}
        )
        assert response.status_code == status.HTTP_200_OK, response.data


@pytest.mark.django_db
class TestPostEmployee:
    def get_post_employee_data(self, buyer_id: int, update_dict: Optional[Dict] = None) -> Dict:
        data = {
            "buyerId": buyer_id,
            "email": "loyal.employee@domain.com",
            "firstName": "Loyal",
            "lastName": "Employee",
            "phoneNumber": "",
            "jobTitle": "",
            "hireDate": None,
            "terminationDate": None,
            "businessUnitId": None,
            "costCenterId": None,
            "coverageGroupId": None,
            "departmentId": None,
            "employeeLevelId": None,
            "geographyId": None,
        }
        if update_dict:
            data.update(update_dict)
        return data

    def test_create_employee(self, user: User, buyer: Buyer) -> None:
        data = self.get_post_employee_data(buyer.id)
        response = employees_test_resource.request("create", user, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED, response.data

    def test_create_employee_duplicate_email(
        self, user: User, buyer: Buyer, employee_factory: TypeEmployeeFactory
    ) -> None:
        employee_factory(email="loyal2.employee@domain.com")
        data = self.get_post_employee_data(buyer.id, {"email": "loyal2.employee@domain.com"})
        response = employees_test_resource.request("create", user, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data
        assert response.data["email"][0] == ErrorDetail(
            string="An employee with that email address already exists.",
            code="unique",
        )

    def test_create_employee_invalid_email_domain(self, user: User, buyer: Buyer) -> None:
        data = self.get_post_employee_data(buyer.id, {"email": "loyal.employee@invaliddomain"})
        response = employees_test_resource.request("create", user, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data
        assert response.data["email"][0] == ErrorDetail(
            string="Enter a valid email address.",
            code="invalid",
        )

    def test_create_employee_invalid_email_no_at(self, user: User, buyer: Buyer) -> None:
        data = self.get_post_employee_data(buyer.id, {"email": "loyal.employee.com"})
        response = employees_test_resource.request("create", user, data=json.dumps(data))
        print(response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data
        assert response.data["email"][0] == ErrorDetail(
            string="Enter a valid email address.",
            code="invalid",
        )
