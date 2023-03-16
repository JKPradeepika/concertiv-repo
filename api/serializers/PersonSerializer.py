from rest_framework import serializers

from api.models.Person import Person


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    phoneNumber = serializers.CharField(source="phone_number", allow_blank=True)
    jobTitle = serializers.CharField(source="job_title", allow_blank=True)
    hireDate = serializers.DateField(source="hire_date", allow_null=True)
    terminationDate = serializers.DateField(source="termination_date", allow_null=True)

    class Meta:
        model = Person
        fields = [
            "id",
            "email",
            "firstName",
            "lastName",
            "employer",
            "phoneNumber",
            "jobTitle",
            "hireDate",
            "terminationDate",
        ]
