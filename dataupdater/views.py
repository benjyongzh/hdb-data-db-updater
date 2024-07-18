from django.http import HttpResponse
import psycopg2
from dotenv import dotenv_values
from django.shortcuts import redirect
from api import views as api_views
from common.util import import_csv_to_db

config = dotenv_values(".env")

# Create your views here.
def update_resale_prices(request):
    if config["ENV"] == "DEV":
        import_csv_to_db("datacollector_resaletransaction", config["RESALE_PRICE_CSV_FOLDER_PATH_DEV"])
    elif config["ENV"] == "PROD":
        import_csv_to_db("datacollector_resaletransaction", config["RESALE_PRICE_CSV_FOLDER_PATH_PROD"])
    return redirect(api_views.get_resale_prices)


#! figure out how to merge new data with building polygons data to create a final table that merges resale prices and building polygons
def update_building_polygons(request):
    return HttpResponse("update building polygons here")