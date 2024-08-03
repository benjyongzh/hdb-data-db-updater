from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .util.csv_operations import update_table_with_csv
from rest_framework.views import APIView
from django.shortcuts import render

from config.env import env

class UploadResaleTransactions(APIView):

    def get(self, request):
        return render(request, 'csv_uploader.html')

    def post(self, request):
        from pathlib import Path
        if request.data['resale_csv_file']:
            csv_file = request.data['resale_csv_file']
            if not csv_file.name.endswith('.csv'):
                return Response({'error': 'File is not CSV.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

            update_table_with_csv("resaletransactions_resaletransaction", csv_file)
            data = {"redirect_url": "/api/resale-transactions/"}
            return Response(data, status=status.HTTP_200_OK)

# Create your views here.
@api_view(['GET'])
def update_new_transactions(request):
    csv_file = request.FILES['csv']
    try:
        update_table_with_csv("resaletransactions_resaletransaction", csv_file)
    except:
        # respond with not ok. wrong config
        data = {"error-message": "Invalid configurations"}
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # respond with ok
    data = {"redirect_url": "/api/resale-transactions/"}
    return Response(data, status=status.HTTP_200_OK)