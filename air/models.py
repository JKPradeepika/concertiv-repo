from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Alliance(models.Model):
    alliance_id = models.IntegerField(primary_key=True)
    alliance_name = models.CharField(max_length=50)

    def __str__(self):
        return self.alliance_id


class Airport(models.Model):
    airport_code = models.CharField(max_length=6, primary_key=True)
    airport_id = models.IntegerField()
    airport_city = models.CharField(max_length=100)

    def __str__(self):
        return self.airport_code

class Airline(models.Model):
    carrier_code = models.CharField(max_length=4,primary_key=True)
    carrier_id = models.IntegerField()
    carrier_name = models.CharField(max_length=100)
    carrier_alliance = models.ForeignKey("Alliance", on_delete=models.CASCADE)

    def __str__(self):
        return self.carrier_code


class FactTable(models.Model):
    id = models.AutoField(primary_key=True)
    data_receive_quarter = models.CharField(max_length=10)
    client_name = models.CharField(max_length=255)
    traveller_name = models.CharField(max_length=255)
    booked_date_or_invoice_date = models.DateField(null=True)
    departure_date = models.DateField()
    carrier_code = models.ForeignKey("Airline", on_delete=models.CASCADE)
    class_of_service_code = models.CharField(max_length=2)
    origin_airport_code = models.ForeignKey("Airport", related_name="origin_airport_code",on_delete=models.CASCADE)
    destination_airport_code = models.ForeignKey("Airport", related_name="destination_airport_code",on_delete=models.CASCADE)
    tour_code = models.CharField(max_length=20, null=True)
    ticket_designator = models.CharField(max_length=20, null=True)
    point_of_sale = models.CharField(max_length=20, null=True)
    fare = models.FloatField()
    tax = models.FloatField()
    miles_or_mileage = models.FloatField()
    pnr_locator = models.CharField(max_length=20, null=True)
    discount = models.FloatField()
    invoice_number = models.CharField(max_length=20, null=True)
    currency_code = models.CharField(max_length=3, null=True)
    
    def __str__(self):
        return self.client_name	