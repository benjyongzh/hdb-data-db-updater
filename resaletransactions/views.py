from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from dotenv import dotenv_values
from common.util.import_csv_to_db import import_from_csv_to_db

config = dotenv_values(".env")

# Create your views here.
@api_view(['GET'])
def update_new_transactions(request):
    if config["ENV"] == "DEV":
        import_from_csv_to_db("resaletransactions_resaletransaction", config["RESALE_PRICE_CSV_FOLDER_PATH_DEV"])
    elif config["ENV"] == "PROD":
        import_from_csv_to_db("resaletransactions_resaletransaction", config["RESALE_PRICE_CSV_FOLDER_PATH_PROD"])
    else:
        # respond with not ok. wrong config
        data = {"error-message": "Invalid configurations"}
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # respond with ok
    data = {"redirect_url": "/api/resale-transactions/"}
    return Response(data, status=status.HTTP_200_OK)


#! figure out how to merge new data with building polygons data to create a final table that merges resale prices and building polygons
def update_building_polygons(request):
    return Response("update building polygons here", status=status.HTTP_200_OK)