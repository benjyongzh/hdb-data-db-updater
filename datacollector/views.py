from django.shortcuts import render
from django.http import HttpResponse

def calculate():
    x=11
    y=2
    return x+ y

# Create your views here.
def get_resale_prices(request):
    return HttpResponse("resale prices here")
def get_building_polygons(request):
    return HttpResponse("building polygons here")