from typing import List

from rest_framework import serializers

from api.models.EmployerCostCenter import EmployerCostCenter
from api.models.EmployerCoverageGroup import EmployerCoverageGroup
from api.models.EmployerDepartment import EmployerDepartment
from api.models.EmployerEmployeeLevel import EmployerEmployeeLevel
from api.models.EmployerGeography import EmployerGeography
from api.models.User import User
from api.serializers.BuyerSerializer import BuyerSerializer


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class UserEmployerCostCenterSerializer(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = EmployerCostCenter
            fields = ["name"]

    class UserEmployeeLevelSerializer(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = EmployerEmployeeLevel
            fields = ["name"]

    class UserCoverageGroupSerializer(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = EmployerCoverageGroup
            fields = ["name"]

    class UserDepartmentSerializer(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = EmployerDepartment
            fields = ["name"]

    class UserGeographySerializer(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = EmployerGeography
            fields = ["name"]

    email = serializers.CharField(source="person.email")
    firstName = serializers.CharField(source="person.first_name")
    lastName = serializers.CharField(source="person.last_name")
    fullName = serializers.CharField(source="person.full_name")
    jobTitle = serializers.CharField(source="person.job_title")
    isStaff = serializers.BooleanField(source="is_staff")
    buyer = BuyerSerializer(source="person.employer.buyer")
    costCenter: UserEmployerCostCenterSerializer = UserEmployerCostCenterSerializer(
        source="person.employee.employer_cost_center"
    )
    employeeLevel: UserEmployeeLevelSerializer = UserEmployeeLevelSerializer(
        source="person.employee.employer_employee_level"
    )
    coverageGroup: UserCoverageGroupSerializer = UserCoverageGroupSerializer(
        source="person.employee.employer_coverage_group"
    )
    department: UserDepartmentSerializer = UserDepartmentSerializer(source="person.employee.employer_department")
    geography: UserGeographySerializer = UserGeographySerializer(source="person.employee.employer_geography")
    groups = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    def get_groups(self, user: User) -> List[str]:
        return [group.name for group in user.groups.all()]

    def get_permissions(self, user: User) -> List[str]:
        return list(user.get_all_permissions())

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "firstName",
            "lastName",
            "fullName",
            "jobTitle",
            "isStaff",
            "buyer",
            "costCenter",
            "employeeLevel",
            "coverageGroup",
            "department",
            "geography",
            "groups",
            "permissions",
        ]


class UserPasswordSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="person.email")

    class Meta:
        model = User
        fields = ["email"]
