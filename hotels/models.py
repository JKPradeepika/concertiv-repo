from django.db import models

# Create your models here.
class Gds_codes(models.Model):
    concertiv_id = models.IntegerField(primary_key=True)
    chain_code = models.CharField(max_length=2)
    chain_name = models.CharField(max_length=255)
    property_name = models.CharField(max_length=255)
    property_address = models.CharField(max_length=255)
    city_name = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    postal_code = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    
    def __str__(self):
        return self.property_name