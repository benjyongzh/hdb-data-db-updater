from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse
from resaletransactions.models import ResaleTransaction


# def calculate():
#     x=11
#     y=2
#     return x+ y

# Create your views here.
def get_resale_prices(request):
    # read from db raw resale prices
    if request.GET.get("latest") == "true":

        #! filter resale_list

        # resale_list = ResaleTransaction.objects.
        resale_list_json = serializers.serialize('json', resale_list)
        return HttpResponse("to show latest here")
    else:
        resale_list = ResaleTransaction.objects.all()
        resale_list_json = serializers.serialize('json', resale_list)
        return HttpResponse(resale_list_json, content_type='application/json')

def get_building_polygons(request):
    # read from db raw resale prices
    return HttpResponse("get building polygons here")