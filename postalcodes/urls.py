from django.urls import path
from . import views

urlpatterns = [
     path('update/postal_codes', views.update_postal_code_data),
     path('update/polygons', views.update_new_building_polygons),
]