from django.urls import path
from . import views

urlpatterns = [
     path('resale-transactions/', views.get_all_resale_prices.as_view(), name='list-resaletransactions'),
     path('resale-transactions/<int:id>/', views.get_resale_price_detail.as_view(), name='list-resaletransactions-detail'),
     path('postal-codes/', views.get_all_postal_codes.as_view(), name='list-postalcodes'),
     path('building-polygons/', views.get_all_building_polygons.as_view(), name='list-polygons'),
     path('resale-transactions/average/<int:timeframe>/', views.average_price_overview.as_view(), name='list-resaletransactions-average'),
     path('resale-transactions/latest/', views.latest_prices.as_view(), name='list-resaletransactions-latest-prices'),
     # path('resale-transactions/latest/avg/', views.latest_price_per_unit.as_view(), name='list-resaletransactions-latest-per-unit'),
]