from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', AdminLogin.as_view(), name='login'),
    path('login/home', AdminLogin.as_view(), name='login_home'),
    path('logout/', AdminLogout.as_view(), name='logout'),
    path('profile/', AdminProfile.as_view(), name='profile'),
    path('create_cpr_user/', CreateUser.as_view(), name='create_cpr_user'),
]
