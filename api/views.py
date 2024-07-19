from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datacollector.models import ResaleTransaction
from postalcodedata.models import PostalCodeAddress
from .serializers import ResaleTransactionSerializer, PostalCodeAddressSerializer

@api_view(['GET'])
def get_resale_prices(request):
    if (request.query_params == {}):
        transactions = ResaleTransaction.objects.all()
    elif (request.query_params['latest'] == 'true'):
        transactions = ResaleTransaction.objects.raw(
        """
        SELECT DISTINCT ON (street_name, block, flat_type, flat_model, storey_range, floor_area_sqm) * FROM
            (SELECT * FROM datacollector_resaletransaction
            ORDER BY street_name, block, flat_type, flat_model, storey_range, floor_area_sqm, month, id DESC)
        orderedbyunitname;
        """)
    else:
        return Response({"message": "Error 400. Invalid URL request."},status=status.HTTP_400_BAD_REQUEST)
        
    serializer = ResaleTransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_postal_codes(request):
    addresses = PostalCodeAddress.objects.all()
    serializer = PostalCodeAddressSerializer(addresses, many=True)
    return Response(serializer.data)