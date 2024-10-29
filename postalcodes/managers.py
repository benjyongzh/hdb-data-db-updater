from django.db.models import Subquery, OuterRef, DecimalField, Value, Avg
from django.db.models.functions import Coalesce
from django.contrib.gis.db import models
from django.apps import apps  # Required for lazy import
from django.contrib.gis.db.models import GeometryField
from django.db.models import Func

class PostalCodeAddressQuerySet(models.QuerySet):

    def with_geometry(self, zoom_level):
        BuildingGeometryPolygon = apps.get_model('postalcodes', 'BuildingGeometryPolygon')
        queryset = BuildingGeometryPolygon.objects.filter(postal_code_key=OuterRef('pk')).values('building_polygon')

        # Determine the simplification tolerance based on the zoom level
        tolerance = self.get_tolerance_from_zoom(zoom_level)
        
        return self.annotate(
        # Simplify the geometry using ST_Simplify with the given tolerance
        # Apply simplification to the geometry
            simplified_geometry=Simplify(Subquery(queryset),tolerance)
        )

    def with_latest_price(self):
        ResaleTransaction = apps.get_model('resaletransactions', 'ResaleTransaction')  # Lazy import of FlatPrice from other app
        queryset = ResaleTransaction.objects \
            .distinct(
                "town",
                "flat_type",
                "block",
                "street_name",
                "floor_area_sqm",
                "storey_range",) \
            .order_by(
                "town",
                "flat_type",
                "block",
                "street_name",
                "floor_area_sqm",
                "storey_range",
                "-id")
        
        # Now, group by townn, block and street_name and calculate the average of the latest resale prices
        latest_price = ResaleTransaction.objects \
            .filter(id__in=Subquery(queryset.only("id"))) \
            .values('town','block','street_name') \
            .annotate(average_latest_price=Avg('resale_price')) \
            .values('average_latest_price')[:1]
        
        return self.annotate(
            latest_price=Coalesce(
                Subquery(latest_price, output_field=DecimalField(max_digits=12, decimal_places=2)),
                Value(0,output_field=DecimalField(max_digits=12, decimal_places=2))
            )
        )
    
    def get_tolerance_from_zoom(self, zoom_level):
        return max(0.001, 0.01 * (15 - zoom_level))
    

    # Custom Simplify class that wraps ST_Simplify (PostGIS function)
class Simplify(Func):
    function = 'ST_Simplify'
    output_field = GeometryField()