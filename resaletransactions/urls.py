from django.urls import path
from . import views

urlpatterns = [
    path('resaleprices/', views.update_resale_prices),# find out how to do params for filtering
    path('buildingpolygons/', views.update_building_polygons),
]