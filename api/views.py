from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from resaletransactions.models import ResaleTransaction
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from .serializers import ResaleTransactionSerializer, PostalCodeAddressSerializer, BuildingGeometryPolygonSerializer
from django.db.models import OuterRef, Subquery, Max, F

class get_all_resale_prices(ListAPIView):
    queryset = ResaleTransaction.objects.all().order_by("id")
    serializer_class = ResaleTransactionSerializer

class get_all_postal_codes(ListAPIView):
    queryset = PostalCodeAddress.objects.all().order_by("id")
    serializer_class = PostalCodeAddressSerializer


class get_all_building_polygons(ListAPIView):
    queryset = BuildingGeometryPolygon.objects.all().order_by("id")
    serializer_class = BuildingGeometryPolygonSerializer

    def get_serializer_context(self):
        # Pass the zoom level to the serializer context
        # zoom_level = int(self.request.query_params.get('zoom', 12))
        zoom_level = 1
        return {'zoom_level': zoom_level}

# return the average price of a block within a past given timeframe
class average_price_overview(APIView):
    def get(self, request, timeframe):
        print(timeframe)

# return the latest price of a block
class latest_price_per_block(ListAPIView):

    latest_transaction = ResaleTransaction.objects \
        .filter(postal_code_key_id=OuterRef('id')) \
        .order_by("-id") \
        .values("resale_price")[:1]
    
    queryset = PostalCodeAddress.objects.annotate(latest_transaction = Subquery(latest_transaction))


    # select latest transaction per block
    """ queryset = ResaleTransaction.objects.distinct(
        "town",
        "flat_type",
        "block",
        "street_name",
        "floor_area_sqm",
        "flat_model",
        "storey_range",).order_by(
        "town",
        "flat_type",
        "block",
        "street_name",
        "floor_area_sqm",
        "flat_model",
        "storey_range",
        "-id") """
    
    '''
    queryset = ResaleTransaction.objects.raw("""
        SELECT
        *
        FROM
            (SELECT
                town,
                flat_type,
                block,
                street_name,
                floor_area_sqm,
                flat_model,
                storey_range,
                MAX(id) AS latest_id
            FROM resaletransactions_resaletransaction
            GROUP BY
                town,
                flat_type,
                block,
                street_name,
                floor_area_sqm,
                flat_model,
                storey_range) LATEST
        INNER JOIN resaletransactions_resaletransaction
        ON LATEST.latest_id = resaletransactions_resaletransaction.id
        ORDER BY LATEST.latest_id
        """
    )
    '''
    
    # join latest_transaction with postalcodeaddress ON same block and street_name
    # join 2nd table with polygons ON same postalcode
    serializer_class = PostalCodeAddressSerializer


class latest_price_per_unit(ListAPIView):
    

    serializer_class = ResaleTransactionSerializer