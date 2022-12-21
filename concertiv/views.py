from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.views.generic.edit import FormView
from django.views.generic import View, TemplateView
from django.template.loader import render_to_string
from django.shortcuts import render
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

from .forms import *
from .models import User

from decouple import config
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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


class AdminLoginView(LoginView):
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
                message = "Please check your username or password."
                return render(request, self.error_url, context={'message': message})
        return render(request, self.template_name, context={'form': form})

class AdminLogoutView(LogoutView):
    template_name = "users/logout.html"
    
    def post(self, request, *args, **kwargs):
        logout(request)
        request.session.clear_expired()
        return render(request, self.template_name)  
    

class AdminProfileView(FormView):
    template_name = "users/profile.html"
    error_url = "commons/error.html"
    
    def get(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            user = User.objects.get(username=username)
            user_email = user.email
            user_role = user.role
            last_login = user.last_login
            return render(request, self.template_name, context={'username': username, 'email': user_email,'role': user_role, 'last_login': last_login})
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})

class CreateUserView(View):
    form_class = UserSignupForm
    confirm_password_form_class = UserPasswordConfirmationForm
    template_name = "users/create_user.html"
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
                    uid = urlsafe_base64_encode(force_bytes(user.id))
                    token = default_token_generator.make_token(user)
                    link = request.build_absolute_uri('create_password/{0}/{1}'.format(uid, token))
                    sender_email = str(config('EMAIL_HOST_USER'))
                    receiver_email = cpr_user_email
                    password = str(config('EMAIL_HOST_PASSWORD'))
                    message = MIMEMultipart("alternative")
                    message["Subject"] = "CPR - Account Creation"
                    message["From"] = sender_email
                    message["To"] = receiver_email
                    html = render_to_string('users/email_confirmation.html', context={'link': link})
                    html_msg = MIMEText(html, "html")
                    message.attach(html_msg)
                    context = ssl.create_default_context()
                    with smtplib.SMTP(str(config('EMAIL_HOST')), port=587) as server:
                        server.starttls(context=context)
                        server.login(sender_email, password)
                        server.sendmail(sender_email, receiver_email, message.as_string())
                    
                    message = 'An Email alert has been sent successfully.'
                    return render(request, self.success_url, context={'message': message, 'username': username})
            else:
                form = self.form_class(request.POST)
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})
        return render(request, self.template_name, context={'form': form, 'username': username})
                    
class AllUsersView(View):
    template_name = 'users/all_users.html'

    def get(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username') 
            request.session.modified = True
            q = User.objects.filter(is_superuser=False)
            user = q.exclude(is_deleted=True)
            return render(request, self.template_name, context={'username': username, 'cpr_user': user})


class UpdateUserView(View):
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
                all_users = User.objects.all().filter(is_deleted=False)
                all_user = all_users.exclude(username=username)
                return render(request, self.all_users_template_name, context={'username': username, 'cpr_user': all_user})
            else:
                form = self.form_class(request.POST)
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})
        return render(request, self.template_name, context={'form': form, 'username': username})
    
    
class DeleteUserView(View):
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
            for user in user_dict:
                user.is_deleted = True
                user.is_active = False
                user.save()
            all_users = User.objects.all().filter(is_deleted=False)
            all_user = all_users.exclude(username=username)
            return render(request, self.all_users_template_name, context={'username': username, 'cpr_user': all_user})
        

class CreatePasswordView(View):
    form_class = UserPasswordConfirmationForm
    template_name = 'users/create_password.html'
    success_url = 'users/account_created.html'
    error_url = 'commons/error.html'
    
    
    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, context={'form': form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            password = request.POST.get('password')
            link = request.POST.get('link')
            user_id = link.split('/')[-2]
            usr_id = urlsafe_base64_decode(user_id).decode('ascii')
            user = User.objects.get(id=usr_id)
            user.password = make_password(password, salt=None, hasher='default')
            user.is_active = True
            user.is_staff = True
            user.save()
            link = link.rsplit('/', 3)
            link = link[0]
            return render(request, self.success_url, context={'link': link})
        else:
            form = self.form_class(request.POST)
        return render(request, self.template_name, context={'form': form})
            
            
class UsersLoginView(AdminLoginView):
    form_class = UserLoginForm
    template_name = 'users/user_login.html'
    error_url = "commons/error.html"
    
    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, context={'form': form})
        
    def post(self, request, *args, **kwargs):
        form = self.get_form_class()
        if self.form_valid:
            user_email = request.POST.get('email')
            user_password = request.POST.get('password')
            email = str(User.objects.get(email=user_email))
            user = authenticate(email=email, password=user_password)
            name = ""
            if user is not None:
                login(request, user)
                user_dict = User.objects.all().filter(email=user)
                for user in user_dict:
                    name = user.username
                    request.session['username'] = name
                return render(request,'commons/home.html' , context={'username': name})
            elif not user:
                message = "Please check your username or password is incorrect."
                return render(request, self.error_url, context={'message': message})
        return render(request, self.template_name, context={'form': form})
    
    
class ResetPasswordView(View):
    form_class = ResetPasswordForm
    template_name = "users/password_reset.html"
    success_url = "users/password_reset_done.html"
    
    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, context={'form': form})        
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                uid = urlsafe_base64_encode(force_bytes(user.id))
                token = default_token_generator.make_token(user)
                link = request.build_absolute_uri('reset_password/{0}/{1}'.format(uid, token))
                home_link = link.rsplit('/', 3)
                portal_link = home_link[0]
                sender_email = str(config('EMAIL_HOST_USER'))
                receiver_email = email
                password = str(config('EMAIL_HOST_PASSWORD'))
                message = MIMEMultipart("alternative")
                message["Subject"] = "CPR - Forgot / Reset Password"
                message["From"] = sender_email
                message["To"] = receiver_email
                html = render_to_string('users/password_reset_email.html', context={'link': link, 'portal_link': portal_link})
                html_msg = MIMEText(html, "html")
                message.attach(html_msg)
                context = ssl.create_default_context()
                with smtplib.SMTP(str(config('EMAIL_HOST')), port=587) as server:
                    server.starttls(context=context)
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message.as_string())
                return render(request, self.success_url)
        else:
            form = self.form_class(request.POST)
        return render(request, self.template_name, context={'form': form})


class ResetPasswordConfirmView(View):
    form_class = ResetPasswordConfirmForm
    template_name = 'users/password_reset_confirm.html'
    success_url = 'users/password_reset_complete.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, context={'form': form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            password = request.POST.get('password')
            link = request.POST.get('link')
            user_id = link.split('/')[-2]
            usr_id = urlsafe_base64_decode(user_id).decode('ascii')
            user = User.objects.get(id=usr_id)
            if user.id:
                user.set_password(password)
                user.save()
            return render(request, self.success_url)
        else:
            form = self.form_class(request.POST)
        return render(request, self.template_name, context={'form': form})
            
            
       