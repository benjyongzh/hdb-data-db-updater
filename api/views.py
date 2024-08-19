from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from resaletransactions.models import ResaleTransaction
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from .serializers import ResaleTransactionSerializer, PostalCodeAddressSerializer, BuildingGeometryPolygonSerializer

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
    def get(self, request):
        timeframe:str = request.query_params['timeframe']
        pass

# return the latest price of a block
class latest_price_overview(ListAPIView):
    # select latest transaction per block
    queryset = ResaleTransaction.objects.order_by(
            "town",
            "flat_type",
            "block",
            "street_name",
            "floor_area_sqm",
            "flat_model",
            "storey_range",
            "-id").distinct(
                "town",
                "flat_type",
                "block",
                "street_name",
                "floor_area_sqm",
                "flat_model",
                "storey_range",)
    
    # join latest_transaction with postalcodeaddress ON same block and street_name
    # join 2nd table with polygons ON same postalcode
    serializer_class = ResaleTransactionSerializer