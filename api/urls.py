from django.urls import path
from . import views

urlpatterns = [
     path('resale-prices/', views.get_resale_prices),
]
