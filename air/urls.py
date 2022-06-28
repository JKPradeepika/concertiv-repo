from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('travel/air/raw-data', views.raw_data, name='raw-data'),
    path('travel/air/process-data', views.process_data, name='process-data'),
    path('travel/air/graphs', views.get_graphs, name='graphs'),
]
