from django.db import models
from django.contrib.gis.db import models

# Create your models here.
class Line(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=5, unique=True)
    color = models.CharField(max_length=7)  # Hex color code

    def __str__(self):
        return self.name

class MrtStation(models.Model):
    name = models.CharField(db_index=True)
    rail_type = models.CharField(max_length=3, db_index=True)#MRT or LRT
    ground_level = models.CharField(max_length=11, db_index=True)#ABOVEGROUND or UNDERGROUND
    lines = models.ManyToManyField(Line, related_name="stations")  # Many-to-Many
    building_polygon = models.PolygonField()

    def __str__(self):
        return f"{self.name} MRT station"
