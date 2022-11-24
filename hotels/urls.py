from django.urls import path
from .views import RawDataView, LoadRawDataView, FuzzyMatchView, CTVGroupSavingsCalculation

app_name = "hotels"

urlpatterns = [
    path('travel/hotels/raw_data', RawDataView.as_view(), name='raw_data'),
    path('travel/hotels/load_raw_data', LoadRawDataView.as_view(), name='load_raw_data'),
    path('travel/hotels/fuzzy_match', FuzzyMatchView.as_view(), name='fuzzy_match'),
    path('travel/hotels/savings_calculation', CTVGroupSavingsCalculation.as_view(), name='savings_calculation'),
]