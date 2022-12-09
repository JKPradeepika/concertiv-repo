from django.urls import path
from .views import *

app_name = 'concertiv'

urlpatterns = [
    path('', AdminLogin.as_view(), name='login'),
    path('home/', HomeView.as_view(), name='home'),
    path('logout/', AdminLogout.as_view(), name='logout'),
    path('profile/', AdminProfile.as_view(), name='profile'),
    path('users/create', CreateUser.as_view(), name='create_user'),
    path('users/all', AllUsers.as_view(), name='all_users'),
    path('users/<int:id>/update', UpdateUser.as_view(), name='update_user'),
    path('users/<int:id>/delete', DeleteUser.as_view(), name='delete_user'),
]
