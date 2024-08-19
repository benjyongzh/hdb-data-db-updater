from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from resaletransactions.models import ResaleTransaction
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from .serializers import ResaleTransactionSerializer, PostalCodeAddressSerializer, BuildingGeometryPolygonSerializer
from django.db.models import Max

class get_all_resale_prices(ListAPIView):
    queryset = ResaleTransaction.objects.all()
    serializer_class = ResaleTransactionSerializer

class get_all_postal_codes(ListAPIView):
    queryset = PostalCodeAddress.objects.all()
    serializer_class = PostalCodeAddressSerializer


class get_all_building_polygons(ListAPIView):
    queryset = BuildingGeometryPolygon.objects.all()
    serializer_class = BuildingGeometryPolygonSerializer

# return the average price of a block within a past given timeframe
class average_price_overview(APIView):
    def get(self, request, timeframe):
        print(timeframe)

# return the latest price of a block
class latest_price_overview(ListAPIView):
    # select latest transaction per block
    # queryset = ResaleTransaction.objects.distinct(
    #     "town",
    #     "flat_type",
    #     "block",
    #     "street_name",
    #     "floor_area_sqm",
    #     "flat_model",
    #     "storey_range",).order_by(
    #     "town",
    #     "flat_type",
    #     "block",
    #     "street_name",
    #     "floor_area_sqm",
    #     "flat_model",
    #     "storey_range",
    #     "-id")
    
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
    
    # join latest_transaction with postalcodeaddress ON same block and street_name
    # join 2nd table with polygons ON same postalcode
    serializer_class = ResaleTransactionSerializer