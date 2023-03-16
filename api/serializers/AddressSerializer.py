from rest_framework import serializers

from api.models.Address import Address


class AddressSerializer(serializers.HyperlinkedModelSerializer):
    street1 = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    country = serializers.CharField()
    postalCode = serializers.CharField(source="postal_code")
    isPrimary = serializers.BooleanField(source="is_primary")

    class Meta:
        model = Address
        fields = [
            "street1",
            "street2",
            "city",
            "state",
            "country",
            "postalCode",
            "isPrimary",
        ]
