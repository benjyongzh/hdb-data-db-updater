from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datacollector.models import ResaleTransaction
from .serializers import ResaleTransactionSerializer

@api_view(['POST'])
def refresh_postal_code_data(request):
    #! from updated resale csv, narrow down to addresses only.
    #! see what addresses are missing in postalcodeaddress table.
    #! for each row missing in table, call openmaps api to get postal code of address.
    #! add address and postal code as new row to postalcodeaddress table.
    #! for each row extra in table, delete row.
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
        
    serializer = ResaleTransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)