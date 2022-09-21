from django.urls import path
from .views import *

app_name = "air"

urlpatterns = [
    path('', HomeView.as_view(), name = 'home'),
    path('travel/air/raw_data', RawDataView.as_view(), name='raw_data'),
    path('travel/air/load_raw_data', LoadRawDataView.as_view(), name='load_raw_data'),
    path('travel/air/process_data', ProcessDataView.as_view(), name='process_data'),
    path('travel/air/graphs', GraphsView.as_view(), name='graphs'),
]
