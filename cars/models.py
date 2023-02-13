from django.db import models

# Create your models here.
class FinalData(models.Model):
    Passenger_name = models.CharField(max_length=255)
    car_details = models.ForeignKey("Details", related_name="rented_car_details",on_delete=models.CASCADE)
    rental_city = models.CharField(max_length=64)
    rental_state = models.CharField(max_length=64)
    rental_date = models.DateField()
    return_date = models.DateField()
    no_of_days = models.IntegerField()
    daily_car_cost = models.IntegerField()
    total_booked_amount = models.FloatField()
    pre_discount = models.FloatField()
    savings = models.FloatField()

    def __str__(self):
        return self.passenger_name

class Details(models.Model):
    car_company_name = models.CharField(max_length=64)
    client_name = models.CharField(max_length=255)
    discount = models.FloatField()
    car_type = models.CharField(max_length=32)

