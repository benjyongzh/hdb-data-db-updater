from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
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