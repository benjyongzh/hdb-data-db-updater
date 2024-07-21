from django.db import models

# Create your models here.
class PostalCodeAddress(models.Model):
    block = models.CharField(max_length=4)
    street_name = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=6)

    def __str__(self):
        return f"Full address of {self.block} {self.street_name} {self.postal_code}"
    
    def get_keys():
        return "block, street_name, postal_code"
    
    def address(self):
        return f"{self.block} {self.street_name}"

