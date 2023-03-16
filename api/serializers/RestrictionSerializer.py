from rest_framework import serializers

from api.models import (
    EmployerCoverageGroup,
    EmployerDepartment,
    EmployerGeography,
)
from api.serializers.validation_helpers import get_nested_instance
from api.helpers import transform_camelcase_to_snakecase


class RestrictionSerializer(serializers.Serializer):
    employerGeographyIds = serializers.ListField(source="employer_geography_ids", required=False)
    employerDepartmentIds = serializers.ListField(source="employer_department_ids", required=False)
    employerCoverageGroupIds = serializers.ListField(source="employer_coverage_group_ids", required=False)

    def validate(self, attrs):
        keys_to_model_classes = {
            "employerGeographyIds": EmployerGeography,
            "employerDepartmentIds": EmployerDepartment,
            "employerCoverageGroupIds": EmployerCoverageGroup,
        }
        for key, model_class in keys_to_model_classes.items():
            snakecase_key = transform_camelcase_to_snakecase(key)
            if snakecase_key in attrs:
                ids_list = attrs.get(snakecase_key, [])
                for id in ids_list:
                    get_nested_instance(model_class, key, id)
        return super().validate(attrs)
