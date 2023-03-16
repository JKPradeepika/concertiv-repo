from rest_framework import serializers

from api.constants import DOMAINS
from api.models.ProductType import ProductType
from api.helpers import ConstantChoiceField


class ProductTypeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    domain = ConstantChoiceField(DOMAINS)

    class Meta:
        model = ProductType
        fields = [
            "id",
            "name",
            "domain",
        ]
