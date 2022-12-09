from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import FormView
from django.views.generic import View, TemplateView

from .forms import *
from .models import User
from decouple import config
import smtplib, ssl
from email.message import EmailMessage

class HomeView(TemplateView):
    template_name = 'commons/home.html'
    error_url = "commons/error.html"
    
    def get(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            return render(request, self.template_name, context={'username': username})
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})


class AdminLogin(LoginView):
    form_class = AdminLoginForm
    template_name = 'users/login.html'
    error_url = "commons/error.html"
    
    def get(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            return render(request, 'commons/home.html',context={'username': username})
        else:
            form = self.form_class
            return render(request, self.template_name, context={'form': form})
        
    def post(self, request, *args, **kwargs):
        form = self.get_form_class()
        if self.form_valid:
            email = request.POST.get('email')
            password = request.POST.get('password')
            email = str(User.objects.get(email=email))
            user = authenticate(email=email, password=password)
            name = ""
            if user is not None:
                login(request, user)
                user_dict = User.objects.all().filter(email=user)
                for user in user_dict:
                    name = user.username
                    request.session['username'] = name
                return render(request,'commons/home.html' , context={'username': name})
            elif not user:
                message = "Unauthorized access. Please login again."
                return render(request, self.error_url, context={'message': message})
        return render(request, self.template_name, context={'form': form})

class AdminLogout(LogoutView):
    template_name = "users/logout.html"
    
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
            user = User.objects.get(id=1)
            user_email = user.email
            user_role = user.role
            last_login = user.last_login
            return render(request, self.template_name, context={'username': username, 'email': user_email,'role': user_role, 'last_login': last_login})
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})

class CreateUser(View):
    form_class = UserSignupForm
    confirm_password_form_class = UserPasswordConfirmationForm
    template_name = "users/create_user.html"
    email_template_name = "users/password_confirm.html"
    success_url = "users/email_sent.html"
    error_url = "commons/error.html"
    
    def get(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            form = self.form_class
            return render(request, self.template_name, context={'form': form, 'username': username})
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})
    
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
                    user.role = "staff"
                    user.save()
                    msg = EmailMessage()
                    msg.set_content("The body of the email is here")
                    msg['Subject'] = "An Email Alert"
                    msg['From'] = config('EMAIL_HOST_USER')
                    msg['To'] = cpr_user_email
                    context = ssl.create_default_context()
                    with smtplib.SMTP("smtp.office365.com", port=587) as smtp:
                        smtp.starttls(context=context)
                        smtp.login(msg['From'], str(config('EMAIL_HOST_PASSWORD')))
                        smtp.send_message(msg)
                    
                    message = 'User created successfully. An Email alert has been sent'
                    return render(request, self.success_url, context={'message': message, 'username': username})
            else:
                form = self.form_class(request.POST)
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})
        return render(request, self.template_name, context={'form': form, 'username': username})
                    
class AllUsers(View):
    template_name = 'users/all_users.html'

    def get(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username') 
            request.session.modified = True
            q = User.objects.filter(is_superuser=False)
            user = q.exclude(is_deleted=True)
            return render(request, self.template_name, context={'username': username, 'cpr_user': user})


class UpdateUser(View):
    form_class = UserUpdateForm
    template_name = 'users/update_user.html'
    all_users_template_name = 'users/all_users.html'
    error_url = "commons/error.html"
    
    def get(self, request, id, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username') 
            request.session.modified = True
            user_dict = User.objects.all().filter(id=id)
            form = self.form_class
            return render(request, self.template_name, context={'form': form, 'username': username, 'cpr_user': user_dict})
    
    def post(self, request, id, *args, **kwargs):
        form = self.form_class(request.POST)
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            if form.is_valid():
                cpr_user_name = request.POST.get('username')
                user_dict = User.objects.all().filter(id=id)
                for user in user_dict:
                    user.username = cpr_user_name
                    user.save()
                user = User.objects.all()
                return render(request, self.all_users_template_name, context={'username': username, 'cpr_user': user})
            else:
                form = self.form_class(request.POST)
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})
        return render(request, self.template_name, context={'form': form, 'username': username})
    
    
class DeleteUser(View):
    template_name = 'users/delete_user.html'
    all_users_template_name = 'users/all_users.html'
    
    def get(self, request, id, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            user_dict = User.objects.all().filter(id=id)
            name = ""
            for user in user_dict:
                name = user.username
            return render(request, self.template_name, context={'username': username, 'delete_user': name})
    
    def post(self, request, id, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            user_dict = User.objects.all().filter(id=id)
            print(user_dict)
            print(type(user_dict))
            for user in user_dict:
                user.is_deleted = True
                user.save()
            all_users = User.objects.all().filter(is_deleted=False)
            return render(request, self.all_users_template_name, context={'username': username, 'cpr_user': all_users})
            