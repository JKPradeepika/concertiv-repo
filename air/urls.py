from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name = 'home'),
    path('travel/air/raw_data', RawDataView.as_view(), name='raw_data'),
    path('travel/air/process_data', ProcessDataView.as_view(), name='process_data'),
]
