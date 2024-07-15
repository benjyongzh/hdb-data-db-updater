from django.urls import path
from . import views

urlpatterns = [
    path('resaleprices/', views.get_resale_prices),#TODO find out how to do params for filtering
    path('buildingpolygons/', views.get_building_polygons),
]

# main display:
# latest transactions per unit (avg across flat_types of same building)
# on click, display all past transactions of unfiltered units of that building

# checkbox filters:
# by town (show/hide)
# by flat_Type (if multiple selected to show then use average for colour display)

# price filter (similar to airbnb slider + bargraph)
