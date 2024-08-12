from django.db import models

# Create your models here.
class TablesLastUpdated(models.Model):
    table = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Timestamp of {self.table} table"