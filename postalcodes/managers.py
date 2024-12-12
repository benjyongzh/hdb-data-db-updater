from django.db.models import Subquery, OuterRef, DecimalField, Avg, Value, Case, When
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

        # Step 2: Map the SQL results to a dictionary for fast lookup
        average_prices = [
            # row[0]: row[1]
            row[1] if row[1] is not None else None
            for row in results
        ]
        # print(average_prices)

        postal_code_price_dict = {}
        for index_block, postal_code in enumerate(list(self.values_list("postal_code",flat=True))):
            for index_price, price in enumerate(average_prices):
                if index_block == index_price:
                    postal_code_price_dict[postal_code] = price
                    break
        # print(postal_code_price_dict)

        # Step 3: Use Case/When expressions to annotate `self` with the average price
        annotations = [
            When(
                postal_code=postalcode,
                then=Value(postal_code_price_dict[postalcode], output_field=DecimalField(max_digits=12, decimal_places=2))
            )
            for postalcode in postal_code_price_dict
        ]

        return self.annotate(
            price=Case(*annotations, default=Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)))
        )