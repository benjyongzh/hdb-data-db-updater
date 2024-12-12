from django.urls import path
from . import views

urlpatterns = [
     path('resale-transactions/', views.get_all_resale_prices.as_view(), name='list-resaletransactions'),
     path('resale-transactions/<int:id>/', views.get_resale_price_detail.as_view(), name='list-resaletransactions-detail'),
     path('postal-codes/', views.get_all_postal_codes.as_view(), name='list-postalcodes'),
     # path('blocks/geometry/', views.stream_polygon_per_block.as_view(), name='list-blocks-geometry'),
     # path('blocks/price/<str:price_type>/', views.price_per_block.as_view(), name='list-blocks-price'),
     path('blocks/geometry/', views.stream_info_per_block.as_view(response_type='geometry'), name='list-blocks-geometry'),
     path('blocks/price/<str:price_type>/', views.stream_info_per_block.as_view(response_type='price'), name='list-blocks-price'),
     path('flat-types/', views.flat_types.as_view(), name='list-flat-types'),
     path('mrt-stations/', views.get_mrt_stations.as_view(), name='list-mrt-stations'),
]