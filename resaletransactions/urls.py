from django.urls import path
from . import views

urlpatterns = [
    path('update/', views.update_new_transactions),# find out how to do params for filtering
]