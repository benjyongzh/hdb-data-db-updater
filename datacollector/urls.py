from django.urls import path
from . import views

urlpatterns = [
    path('resaleprices/', views.get_resale_prices),
    path('buildingpolygons/', views.get_building_polygons),
]