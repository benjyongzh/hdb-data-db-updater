from django.urls import path
from . import views

urlpatterns = [
     path('refresh/', views.refresh_postal_code_data),
]