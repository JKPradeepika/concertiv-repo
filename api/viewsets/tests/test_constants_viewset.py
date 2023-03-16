import pytest
from typing import Any, List, Tuple
from rest_framework import status

from api.constants import CONSTANTS_OBJECTS
from api.viewsets import ConstantViewSet
from api.viewsets.tests.viewset_test_helpers import ViewSetTestResource


def get_constant_names_id_values() -> List[Tuple[str, int, Any]]:
    """For all constant categories, return all valid ids and values."""
    consts_name_id_values = []
    for constant_name in CONSTANTS_OBJECTS:
        for item in CONSTANTS_OBJECTS[constant_name]:
            if isinstance(CONSTANTS_OBJECTS[constant_name], tuple):
                id, value = item[0], {"id": item[0], "name": item[1]}
            else:
                id = item
                value = CONSTANTS_OBJECTS[constant_name][item]
            consts_name_id_values.append((constant_name, id, value))
    return consts_name_id_values


class TestConstantsViewset:
    @pytest.mark.parametrize("constant_name", CONSTANTS_OBJECTS.keys())
    def test_constant_endpoint_list(self, constant_name: str) -> None:
        constant_test_resource = ViewSetTestResource(ConstantViewSet, f"{constant_name}-list")
        response = constant_test_resource.request("list", basename=constant_name)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(["constant_name", "subconstant_id", "subconstant_value"], get_constant_names_id_values())
    def test_constant_endpoint_get(self, constant_name: str, subconstant_id: int, subconstant_value: Any) -> None:
        constant_test_resource = ViewSetTestResource(ConstantViewSet, f"{constant_name}-list")
        response = constant_test_resource.request("retrieve", basename=constant_name, pk=str(subconstant_id))
        assert response.status_code == status.HTTP_200_OK
        assert response.data == subconstant_value
