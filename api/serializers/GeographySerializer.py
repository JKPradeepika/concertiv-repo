from rest_framework import serializers

from api.models.Geography import Geography


class GeographySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Geography
        fields = ["id", "name"]
