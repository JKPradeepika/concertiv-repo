from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login, logout
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import TemplateView

from .forms import *
from .models import *
from django.contrib.auth.models import User


class AdminLogin(LoginView):
    form_class = AdminLoginForm
    template_name = 'users/admin_login.html'
    success_url = 'commons/home.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, context={'form': form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        username = str(User.objects.get(username=username))
        user = authenticate(username=username, password=password)
        if not user:
            message = "Invalid login credentials. Please try again."
        if user is not None:
            login(request, user)
            request.session['username'] = username
            return render(request, self.success_url, context={'username': username})
        return render(request, self.template_name, context={'form': form, 'message': message})

class AdminLogout(LogoutView):
    template_name = "commons/home.html"
    
    def post(self, request, *args, **kwargs):
        logout(request)
        return render(request, self.template_name)  
    

class AdminProfile(DetailView, FormView):
    template_name = "users/profile.html"
    error_url = "commons/error.html"
    
    def get(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            email = request.user.email
            if request.user.is_superuser:
                request.session['role'] = 'superuser'
            else:
                request.session['role'] = 'user'
            last_login = request.user.last_login
            return render(request, self.template_name, context={'username': username, 'email': email,'role': request.session.get('role'), 'last_login': last_login})
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})

class CreateUser(CreateView):
    form_class = UserSignupForm
    template_name = "users/create_user.html"
    error_url = "commons/error.html"
    
    def get(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            form = self.form_class
            return render(request, self.template_name, context={'form': form, 'username': username})
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})