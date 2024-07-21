from django.urls import path
from . import views

urlpatterns = [
    path('update-new-transactions/', views.update_new_transactions),# find out how to do params for filtering
    path('buildingpolygons/', views.update_building_polygons),
]