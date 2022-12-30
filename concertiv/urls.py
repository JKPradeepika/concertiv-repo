from django.urls import path
from .views import *

app_name = 'concertiv'

urlpatterns = [
    path('', AdminLoginView.as_view(), name='login'),
    path('home/', HomeView.as_view(), name='home'),
    path('logout/', AdminLogoutView.as_view(), name='logout'),
    path('profile/', AdminProfileView.as_view(), name='profile'),
    path('users/create', CreateUserView.as_view(), name='create_user'),
    path('users/all', AllUsersView.as_view(), name='all_users'),
    path('users/update/<int:id>', UpdateUserView.as_view(), name='update_user'),
    path('users/delete/<int:id>', DeleteUserView.as_view(), name='delete_user'),
    path('users/create_password/<uidb64>/<token>', CreatePasswordView.as_view(), name='create_password'),
    path('users/', UsersLoginView.as_view(), name='user_login'),
    path('users/reset_password', ResetPasswordView.as_view(), name='reset_password'),
    path('users/reset_password/<uidb64>/<token>', ResetPasswordConfirmView.as_view(), name='reset_password_done'),
    path('users/logout', UsersLogoutView.as_view(), name='user_logout'),
]