from django.db.models import Subquery, OuterRef, DecimalField, Value, Avg, F
from django.db.models.functions import RowNumber,Coalesce
from django.db.models.expressions import Window
from django.contrib.gis.db import models
from django.apps import apps  # Required for lazy import

class PostalCodeAddressQuerySet(models.QuerySet):

    def with_geometry(self):
        BuildingGeometryPolygon = apps.get_model('postalcodes', 'BuildingGeometryPolygon')
        queryset = BuildingGeometryPolygon.objects.filter(postal_code_key=OuterRef('pk')).values('building_polygon')
        
        return self.annotate(
        # Simplify the geometry using ST_Simplify with the given tolerance
            geometry=Subquery(queryset) # this is working well. need to simplify this geometry
        )

    def with_latest_price(self):
        ResaleTransaction = apps.get_model('resaletransactions', 'ResaleTransaction')  # Lazy import of FlatPrice from other app  
        # TODO fix latest_price always being same number
            
        queryset = ResaleTransaction.objects \
            .distinct(
                'postal_code_key',
                "town",
                "flat_type",
                "block",
                "street_name",
                "floor_area_sqm",
                "storey_range",) \
            .order_by(
                'postal_code_key',
                "town",
                "flat_type",
                "block",
                "street_name",
                "floor_area_sqm",
                "storey_range",
                "-id")
        
        latest_prices = ResaleTransaction.objects \
            .filter(id__in=Subquery(queryset.only("id"))) \
            .values('postal_code_key') \
            .annotate(average_latest_price=Avg('resale_price'))
            # .values('average_latest_price')

        print(latest_prices)
        
        return self.annotate(
            # latest_price=Subquery(latest_prices.filter(postal_code_key=OuterRef('pk')).values('average_latest_price')[:1])
            latest_price=Subquery(ResaleTransaction.objects.filter(postal_code_key=Subquery(latest_prices).postal_code_key).values('average_latest_price')[:1])
            # latest_price=Coalesce(
            #     Subquery(latest_price, output_field=DecimalField(max_digits=12, decimal_places=2)),
            #     Value(0,output_field=DecimalField(max_digits=12, decimal_places=2))
            # )
        )