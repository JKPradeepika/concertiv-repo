from rest_framework import serializers

from api.models.Contact import Contact


class ContactSerializer(serializers.HyperlinkedModelSerializer):
    email = serializers.CharField(source="person.email")
    firstName = serializers.CharField(source="person.first_name")
    lastName = serializers.CharField(source="person.last_name")
    fullName = serializers.CharField(source="person.full_name")
    phoneNumber = serializers.CharField(source="person.phone_number")
    isPrimary = serializers.BooleanField(source="is_primary")

    class Meta:
        model = Contact
        fields = [
            "email",
            "firstName",
            "lastName",
            "fullName",
            "phoneNumber",
            "description",
            "isPrimary",
        ]
