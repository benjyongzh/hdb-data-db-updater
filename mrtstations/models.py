from django.db import models
from django.contrib.gis.db import models

# Create your models here.
class MrtStation(models.Model):
    name = models.CharField(db_index=True)
    rail_type = models.CharField(max_length=3, db_index=True)#MRT or LRT
    ground_level = models.CharField(max_length=11, db_index=True)#ABOVEGROUND or UNDERGROUND
    building_polygon = models.PolygonField()

    def __str__(self):
        return f"{self.name} MRT station"
