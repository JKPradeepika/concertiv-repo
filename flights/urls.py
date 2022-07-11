from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('travel/airlines/raw-data', views.raw_data, name='raw-data'),
    path('travel/airlines/process-data', views.process_data, name='process-data'),
    path('travel/airlines/graphs', views.get_graphs, name='graphs'),
]
