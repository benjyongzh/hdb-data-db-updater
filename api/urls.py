from django.urls import path
from . import views

urlpatterns = [
     path('resale-prices/', views.get_resale_prices),
]

urlpatterns = [
     path('postal-codes/', views.get_postal_codes),
]