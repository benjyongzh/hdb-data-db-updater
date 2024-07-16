from rest_framework.response import Response
from rest_framework.decorators import api_view
from datacollector.models import ResaleTransaction
from .serializers import ResaleTransactionSerializer

@api_view(['GET'])
def get_resale_prices(request):
    transactions = ResaleTransaction.objects.all()
    serializer = ResaleTransactionSerializer(transactions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_resale_prices_latest(request):
    #! to use sql to filter results
    # transactions = ResaleTransaction.objects.all()
    # serializer = ResaleTransactionSerializer(transactions, many=True)
    return Response("hi")