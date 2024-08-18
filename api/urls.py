from django.urls import path
from . import views

urlpatterns = [
     path('resale-transactions/', views.get_resale_prices),
     path('postal-codes/', views.get_postal_codes),
     path('building-polygons/', views.get_building_polygons),
     path('resale-transactions/latest', views.latest_price_overview.as_view()),
]