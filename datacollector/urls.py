from django.urls import path
from . import views

urlpatterns = [
    path('resaleprices/', views.get_resale_prices),# find out how to do params for filtering
    path('buildingpolygons/', views.get_building_polygons),
]