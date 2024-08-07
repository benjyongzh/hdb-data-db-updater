from django.db import models

# Create your models here.
class ResaleTransaction(models.Model):
    month = models.CharField(max_length=7)
    town = models.CharField(max_length=100)
    flat_type = models.CharField(max_length=50)
    block = models.CharField(max_length=4)
    street_name = models.CharField(max_length=100)
    storey_range = models.CharField(max_length=10)
    floor_area_sqm = models.DecimalField(max_digits=7, decimal_places=2)
    flat_model = models.CharField( max_length=50)
    lease_commence_date = models.CharField(max_length=4)
    remaining_lease = models.CharField(max_length=100)
    resale_price = models.DecimalField(max_digits=12, decimal_places=2)


    def __str__(self):
        return f"{self.town} {self.block} {self.month} {self.resale_price}"
    
    def get_keys():
        return "month, town, flat_type, block, street_name, storey_range, floor_area_sqm, flat_model, lease_commence_date, remaining_lease, resale_price"
    
    def age_on_purchase(self):
        return 99 - int(self.remaining_lease)
    
    def address(self):
        return f"{self.block} {self.street_name}"

