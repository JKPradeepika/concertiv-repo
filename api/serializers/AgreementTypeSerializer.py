from rest_framework import serializers

from api.models.AgreementType import AgreementType


class AgreementTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AgreementType
        fields = [
            "id",
            "name",
        ]
