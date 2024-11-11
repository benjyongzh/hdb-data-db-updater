from django.db.models import Subquery, OuterRef, DecimalField, Avg, Value, Case, When ,Q
from django.db.models.functions import RowNumber,Coalesce
from django.db.models.expressions import Window
from django.contrib.gis.db import models
from django.apps import apps  # Required for lazy import
from django.db import connection

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
            
        # queryset = ResaleTransaction.objects \
        #     .distinct(
        #         'postal_code_key',
        #         "town",
        #         "flat_type",
        #         "block",
        #         "street_name",
        #         "floor_area_sqm",
        #         "storey_range",) \
        #     .order_by(
        #         'postal_code_key',
        #         "town",
        #         "flat_type",
        #         "block",
        #         "street_name",
        #         "floor_area_sqm",
        #         "storey_range",
        #         "-id")
        # latest_prices = ResaleTransaction.objects \
        #     .filter(id__in=Subquery(queryset.only("id"))) \
        #     .values('postal_code_key') \
        #     .annotate(average_latest_price=Avg('resale_price'))
            # .values('postal_code_key', 'average_latest_price')

        # price_map = list(latest_prices)
        # print(price_map)

        # return self.annotate(
        #     latest_price=Subquery(
        #         latest_prices.filter(postal_code_key=OuterRef('postal_code'))
        #         .values('average_latest_price')[:1]
        #     )
            # latest_price=Coalesce(
            #     Subquery(latest_price, output_field=DecimalField(max_digits=12, decimal_places=2)),
            #     Value(0,output_field=DecimalField(max_digits=12, decimal_places=2))
            # )
        # )

        with connection.cursor() as cursor:
            cursor.execute("""
                WITH latest_transactions AS (
                    SELECT DISTINCT ON (postal_code_key_id, flat_type, storey_range, floor_area_sqm)
                        postal_code_key_id,
                        town,
                        block,
                        street_name,
                        flat_type,
                        storey_range,
                        floor_area_sqm,
                        resale_price
                    FROM
                        resaletransactions_resaletransaction
                    ORDER BY 
                        postal_code_key_id, flat_type, storey_range, floor_area_sqm, id DESC
                )
                SELECT
                    postal_code_key_id,
                    AVG(resale_price) AS average_price
                FROM
                    latest_transactions
                GROUP BY
                    postal_code_key_id;
            """)
            results = cursor.fetchall()

        # print("SQL Query Results:", results)

        # Step 2: Map the SQL results to a dictionary for fast lookup
        average_prices = {
            row[0]: row[1] if row[1] is not None else None  # (postal_code_key_id) -> average_price
            for row in results
        }

        print(list(average_prices.items()))

        # Step 3: Use Case/When expressions to annotate `self` with the average price
        annotations = [
            When(
                postal_code=postal_code_key_id,
                then=Value(average_price, output_field=DecimalField(max_digits=12, decimal_places=2))
            )
            for postal_code_key_id, average_price in list(average_prices.items()) if average_price is not None
        ]

        return self.annotate(
            latest_price=Case(*annotations, default=Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)))
            # ! always getting default only
        )