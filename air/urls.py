from django.urls import path
from .views import RawDataView, LoadRawDataView, ProcessDataView

app_name = "air"

urlpatterns = [
    path('travel/air/raw_data', RawDataView.as_view(), name='raw_data'),
    path('travel/air/load_raw_data', LoadRawDataView.as_view(), name='load_raw_data'),
    path('travel/air/process_data', ProcessDataView.as_view(), name='process_data'),
]
