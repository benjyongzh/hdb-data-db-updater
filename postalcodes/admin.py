from django.contrib import admin
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon

class PostalCodeAddressAdmin(admin.ModelAdmin):
    list_display = ['block', 'street_name', 'postal_code']

    
class BuildingGeometryPolygonAdmin(admin.ModelAdmin):
    list_display = ['block', 'postal_code', 'building_polygon']

# Register your models here.
admin.site.register(PostalCodeAddress,PostalCodeAddressAdmin)
admin.site.register(BuildingGeometryPolygon,BuildingGeometryPolygonAdmin)