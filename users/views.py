from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import FormView
from django.views.generic import View, TemplateView

from .forms import *
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from CPR.settings import dev


class HomeView(TemplateView):
    template_name = 'commons/home.html'


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
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})
        if user is not None:
            login(request, user)
            request.session['username'] = username
            return render(request, self.success_url, context={'username': username})
        return render(request, self.template_name, context={'form': form})

class AdminLogout(LogoutView):
    template_name = "commons/home.html"
    
    def post(self, request, *args, **kwargs):
        logout(request)
        request.session.clear_expired()
        return render(request, self.template_name)  
    

class AdminProfile(FormView):
    template_name = "users/profile.html"
    error_url = "commons/error.html"
    
    def get(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
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

class CreateUser(View):
    form_class = UserSignupForm
    template_name = "users/create_user.html"
    success_url = "users/success.html"
    error_url = "commons/error.html"
    
    def get(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            form = self.form_class
            return render(request, self.template_name, context={'form': form, 'username': username})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            if form.is_valid():
                cpr_user_name = request.POST.get('username')
                cpr_user_email = request.POST.get('email')
                if not User.objects.filter(username=cpr_user_name).exists():
                    user = User.objects.create_user(username=cpr_user_name, email=cpr_user_email)
                    user.is_active = False
                    user.save()
                    subject = 'Test Email'
                    body = 'Test'
                    email = EmailMessage(
                        subject,
                        body,
                        dev.EMAIL_HOST_USER,
                        [cpr_user_email],
                    )
                    email.send(fail_silently=False)
                    message = 'User created successfully'
                    return render(request, self.success_url, context={'message': message})
            else:
                form = self.form_class(request.POST)
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})
        return render(request, self.template_name, context={'form': form, 'username': username})
                    
        