from django.urls import path
from .views import SignUpView

urlpatterns = [
    path('user/signup/', SignUpView.as_view(), name='signup'),
]