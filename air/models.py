from django.db import models

# Create your models here.
class Alliance(models.Model):
    alliance_id = models.IntegerField(primary_key=True)
    alliance_name = models.CharField(max_length=50)

    def __str__(self):
        return self.alliance_name


class Airport(models.Model):
    airport_id = models.IntegerField()
    airport_code = models.CharField(max_length=6, primary_key=True)
    airport_city = models.CharField(max_length=100)

    def __str__(self):
        return self.airport_city

class Airline(models.Model):
    carrier_id = models.IntegerField()
    carrier_name = models.CharField(max_length=100)
    carrier_code = models.CharField(max_length=4, primary_key=True, unique=True)
    alliance_id = models.ForeignKey("Alliance", verbose_name="alliance_id", on_delete=models.CASCADE)

    def __str__(self):
        return self.carrier_name