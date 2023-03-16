from rest_framework import serializers

from api.models.BusinessType import BusinessType


class BusinessTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BusinessType
        fields = [
            "id",
            "name",
        ]
