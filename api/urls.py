from django.urls import path
from . import views

urlpatterns = [
     path('resale-transactions/', views.get_all_resale_prices.as_view(), name='list-resaletransactions'),
     path('resale-transactions/<int:id>/', views.get_resale_price_detail.as_view(), name='list-resaletransactions-detail'),
     path('postal-codes/', views.get_all_postal_codes.as_view(), name='list-postalcodes'),
     path('building-polygons/', views.get_all_building_polygons.as_view(), name='list-polygons'),
     path('resale-transactions/average/', views.average_prices.as_view(), name='list-resaletransactions-average'),
     path('resale-transactions/latest/', views.latest_prices.as_view(), name='list-resaletransactions-latest'),
     path('resale-transactions/latest-avg/', views.latest_avg_per_block.as_view(), name='list-resaletransactions-latest-average'),
     path('polygons/latest-avg/', views.stream_polygon_price_per_block.as_view(), name='list-polygons-latest-average'),
]