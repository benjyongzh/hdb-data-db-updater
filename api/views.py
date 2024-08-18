from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from resaletransactions.models import ResaleTransaction
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from .serializers import ResaleTransactionSerializer, PostalCodeAddressSerializer, BuildingGeometryPolygonSerializer

@api_view(['GET'])
def get_resale_prices(request):
    if (request.query_params == {}):
        transactions = ResaleTransaction.objects.all()
    elif (request.query_params['latest'] == 'true'):
        transactions = ResaleTransaction.objects.order_by(
            "street_name",
            "block",
            "flat_type",
            "flat_model",
            "storey_range",
            "floor_area_sqm",
            "month",
            "-id").distinct(
                "street_name",
                "block",
                "flat_type",
                "flat_model",
                "storey_range",
                "floor_area_sqm")
    else:
        return Response({"message": "Error 400. Invalid URL request."},status=status.HTTP_400_BAD_REQUEST)
        
    serializer = ResaleTransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_postal_codes(request):
    addresses = PostalCodeAddress.objects.all()
    serializer = PostalCodeAddressSerializer(addresses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_building_polygons(request):
    polygons = BuildingGeometryPolygon.objects.all()
    serializer = BuildingGeometryPolygonSerializer(polygons, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

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