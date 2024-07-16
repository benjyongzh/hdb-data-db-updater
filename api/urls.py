from django.urls import path
from . import views

urlpatterns = [
     path('', views.get_resale_prices),
     path('latest/', views.get_resale_prices_latest)
]
