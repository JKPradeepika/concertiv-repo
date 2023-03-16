from django_filters import rest_framework as filters

from api.models.Geography import Geography


class GeographyFilterSet(filters.FilterSet):
    class Meta:
        model = Geography
        fields = {
            "id": ["exact"],
            "name": ["exact", "icontains"],
        }
