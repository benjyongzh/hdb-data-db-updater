from django.db import models
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from .managers import PostalCodeAddressQuerySet

def postal_code_validation(value:str):
    if len(value) != 6 or not value.isdigit():
        raise ValidationError(f"{value} is an invalid postal code.")

# Create your models here.
class PostalCodeAddress(models.Model):
    block = models.CharField(max_length=4, db_index=True)
    street_name = models.CharField(max_length=100, db_index=True)
    postal_code = models.CharField(validators=[postal_code_validation])

    def __str__(self):
        return f"Full address of {self.block} {self.street_name} {self.postal_code}"
    
    def get_keys():
        return "block, street_name, postal_code"
    
    def address(self):
        return f"{self.block} {self.street_name}"
    
    # Use the custom QuerySet for the model
    objects = PostalCodeAddressQuerySet.as_manager()

class BuildingGeometryPolygon(models.Model):
    block = models.CharField(max_length=4, db_index=True)
    postal_code = models.CharField(validators=[postal_code_validation], db_index=True)
    postal_code_key = models.ForeignKey('postalcodes.PostalCodeAddress', related_name='buildinggeometrypolygons', default=None, on_delete=models.PROTECT, null=True)
    building_polygon = models.PolygonField()

    def __str__(self):
        return f"Building polygon of {self.postal_code}"
    
    def get_keys():
        return "postal_code, building_polygon"
    
    def polygon(self):
        return self.building_polygon

