from django.db import models
from django.db.models import Case, QuerySet, Value, When
from rest_framework import viewsets

from api.filtersets import EmployeeFilterSet
from api.models.Employee import Employee
from api.policies import CustomDjangoModelPermissions, EmployeeAccessPolicy
from api.serializers.EmployeeSerializer import EmployeeSerializer
from api.viewsets.ViewSetHelpers import PageSetPagination, sort_and_filter_queryset

column_name_mappings = {
    "lastname": "person__last_name",
    "firstname": "person__first_name",
    "email": "person__email",
    "phonenumber": "person__phone_number",
    "jobtitle": "person__job_title",
    "hiredate": "person__hire_date",
    "terminationdate": "person__termination_date",
    "employmentstatus": "person__employment_status",
    "employeelevel": "employer_employee_level__name",
    "geography": "employer_geography__name",
    "coveragegroup": "employer_coverage_group__name",
    "department": "employer_department__name",
    "costcenter": "employer_cost_center__name",
    "businessunit": "employer_business_unit__name",
}


class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomDjangoModelPermissions, EmployeeAccessPolicy]
    filterset_class = EmployeeFilterSet
    pagination_class = PageSetPagination

    # Ensure that current user can only see the models they are allowed to see
    def get_queryset(self) -> QuerySet[Employee]:
        queryset = (
            Employee.objects.order_by("id").prefetch_related(
                "person",
                "employer_employee_level",
                "employer_employee_level__employee_level",
                "employer_cost_center",
                "employer_coverage_group",
                "employer_department",
                "employer_geography",
            )
            # only necessary because person.employment_status is a property, which is not q-filterable
            .annotate(
                person__employment_status=Case(
                    When(person__termination_date__isnull=False, then=Value("TERMINATED")),
                    default=Value("ACTIVE"),
                    outfield_field=models.TextField(),
                )
            )
        )
        queryset = sort_and_filter_queryset(
            initial_queryset=queryset, column_name_mappings=column_name_mappings, query_params=self.request.query_params
        )
        return EmployeeAccessPolicy.scope_queryset(self.request, queryset)

    serializer_class = EmployeeSerializer
