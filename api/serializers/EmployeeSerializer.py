from typing import Any, Dict

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.constants import EMPLOYMENT_STATUSES
from api.models.Employee import Employee
from api.models.Employer import Employer
from api.models.EmployerBusinessUnit import EmployerBusinessUnit
from api.models.EmployerCostCenter import EmployerCostCenter
from api.models.EmployerCoverageGroup import EmployerCoverageGroup
from api.models.EmployerDepartment import EmployerDepartment
from api.models.EmployerEmployeeLevel import EmployerEmployeeLevel
from api.models.EmployerGeography import EmployerGeography
from api.models.Person import Person
from api.serializers.EmployerBusinessUnitSerializer import EmployerBusinessUnitSerializer
from api.serializers.EmployerCostCenterSerializer import EmployerCostCenterSerializer
from api.serializers.EmployerCoverageGroupSerializer import EmployerCoverageGroupSerializer
from api.serializers.EmployerDepartmentSerializer import EmployerDepartmentSerializer
from api.serializers.EmployerEmployeeLevelSerializer import EmployerEmployeeLevelSerializer
from api.serializers.EmployerGeographySerializer import EmployerGeographySerializer
from api.serializers.PersonSerializer import PersonSerializer


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):

    buyerId = serializers.IntegerField(source="person.employer.buyer.pk")
    email = serializers.EmailField(
        source="person.email",
        max_length=Person._meta.get_field("email").max_length,
        validators=[
            UniqueValidator(
                queryset=Person.objects.all(), message=_("An employee with that email address already exists.")
            )
        ],
    )
    firstName = serializers.CharField(source="person.first_name")
    lastName = serializers.CharField(source="person.last_name")
    phoneNumber = serializers.CharField(source="person.phone_number", allow_blank=True)
    jobTitle = serializers.CharField(source="person.job_title", allow_blank=True)
    hireDate = serializers.DateField(source="person.hire_date", allow_null=True)
    terminationDate = serializers.DateField(source="person.termination_date", allow_null=True)
    businessUnit = EmployerBusinessUnitSerializer(source="employer_business_unit", read_only=True)
    businessUnitId = serializers.PrimaryKeyRelatedField(
        source="employer_business_unit", queryset=EmployerBusinessUnit.objects.all(), write_only=True, allow_null=True
    )
    costCenter = EmployerCostCenterSerializer(source="employer_cost_center", read_only=True)
    costCenterId = serializers.PrimaryKeyRelatedField(
        source="employer_cost_center", queryset=EmployerCostCenter.objects.all(), write_only=True, allow_null=True
    )
    coverageGroup = EmployerCoverageGroupSerializer(source="employer_coverage_group", read_only=True)
    coverageGroupId = serializers.PrimaryKeyRelatedField(
        source="employer_coverage_group", queryset=EmployerCoverageGroup.objects.all(), write_only=True, allow_null=True
    )
    department = EmployerDepartmentSerializer(source="employer_department", read_only=True)
    departmentId = serializers.PrimaryKeyRelatedField(
        source="employer_department", queryset=EmployerDepartment.objects.all(), write_only=True, allow_null=True
    )
    employeeLevel = EmployerEmployeeLevelSerializer(source="employer_employee_level", read_only=True)
    employeeLevelId = serializers.PrimaryKeyRelatedField(
        source="employer_employee_level", queryset=EmployerEmployeeLevel.objects.all(), write_only=True, allow_null=True
    )
    employmentStatus = serializers.SerializerMethodField()
    geography = EmployerGeographySerializer(source="employer_geography", read_only=True)
    geographyId = serializers.PrimaryKeyRelatedField(
        source="employer_geography", queryset=EmployerGeography.objects.all(), write_only=True, allow_null=True
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "buyerId",
            "email",
            "firstName",
            "lastName",
            "phoneNumber",
            "jobTitle",
            "hireDate",
            "terminationDate",
            "businessUnit",
            "businessUnitId",
            "costCenter",
            "costCenterId",
            "coverageGroup",
            "coverageGroupId",
            "department",
            "departmentId",
            "employeeLevel",
            "employeeLevelId",
            "employmentStatus",
            "geography",
            "geographyId",
        ]

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> Employee:
        person_data = validated_data.pop("person")
        business_unit = validated_data.pop("businessUnitId", None)
        cost_center = validated_data.pop("costCenterId", None)
        coverage_group = validated_data.pop("coverageGroupId", None)
        employee_level = validated_data.pop("employeeLevelId", None)
        geography = validated_data.pop("geographyId", None)

        employer = Employer.objects.get(buyer__id=person_data["employer"]["buyer"]["pk"])
        person_data["employer"] = employer

        person = PersonSerializer().create(person_data)
        validated_data["person"] = person

        if business_unit:
            validated_data["businessUnit"] = business_unit
        if cost_center:
            validated_data["costCenter"] = cost_center
        if coverage_group:
            validated_data["coverageGroup"] = coverage_group
        if employee_level:
            validated_data["employeeLevel"] = employee_level
        if geography:
            validated_data["geography"] = geography

        return Employee.objects.create(**validated_data)

    @transaction.atomic
    def update(self, instance: Employee, validated_data: Dict[str, Any]) -> Employee:
        person_data = validated_data.pop("person")

        # Get Employer from BuyerId
        employer = Employer.objects.get(buyer__id=person_data["employer"]["buyer"]["pk"])
        person_data["employer"] = employer

        # update Person
        PersonSerializer().update(instance.person, person_data)

        # Update direct fields for Employee
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    @staticmethod
    def get_employmentStatus(obj):
        employment_status = obj.employment_status
        if employment_status:
            return {"id": employment_status, "name": dict(EMPLOYMENT_STATUSES)[employment_status]}
        return None
