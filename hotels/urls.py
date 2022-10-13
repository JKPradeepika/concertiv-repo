from django.urls import path
from .views import *

app_name = "hotels"

urlpatterns = [
    path('travel/hotels/raw_data', RawDataView.as_view(), name='raw_data'),
]