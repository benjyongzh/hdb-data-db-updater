from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datacollector.models import ResaleTransaction
from .serializers import ResaleTransactionSerializer

@api_view(['GET'])
def get_resale_prices(request):
    if (request.query_params == {}):
        transactions = ResaleTransaction.objects.all()
    elif (request.query_params['latest'] == 'true'):
        transactions = ResaleTransaction.objects.raw(
        """
        SELECT DISTINCT ON (full_unit_name) * FROM
            (SELECT id, month, town, (
                SELECT street_name
                || ' ' || block
                || ' ' || flat_type
                || ' ' || flat_model
                || ' ' || storey_range
                || ' ' || floor_area_sqm AS full_unit_name),
            resale_price FROM datacollector_resaletransaction
            ORDER BY full_unit_name, month, id DESC) 
        orderedbyunitname;
        """)
    else:
        return Response({"message": "Error 400. Invalid URL request."},status=status.HTTP_400_BAD_REQUEST)
        
    serializer = ResaleTransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['GET'])
# def get_resale_prices_latest(request):
    
#     serializer = ResaleTransactionSerializer(transactions, many=True)
#     return Response(serializer.data)