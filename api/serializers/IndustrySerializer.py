from rest_framework import serializers

from api.constants import DOMAINS
from api.models.Industry import Industry
from api.helpers import ConstantChoiceField


class IndustrySerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    domain = ConstantChoiceField(DOMAINS)

    class Meta:
        model = Industry
        fields = [
            "id",
            "name",
            "domain",
        ]
