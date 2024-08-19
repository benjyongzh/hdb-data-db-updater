from django.urls import path
from . import views

urlpatterns = [
     path('resale-transactions/', views.get_all_resale_prices.as_view()),
     path('postal-codes/', views.get_all_postal_codes.as_view()),
     path('building-polygons/', views.get_all_building_polygons.as_view()),
     path('resale-transactions/latest', views.latest_price_overview.as_view()),
]