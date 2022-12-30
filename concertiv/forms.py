from django import forms
import re


class AdminLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Enter Email', 'text-align': 'center'}), label='Email', max_length=60, required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter Password', 'text-align': 'center'}), label='Password', max_length=10, required=True)
 

class UserSignupForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter Name', 'text-align': 'center'}), label='Name', max_length=50, required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Enter Email', 'text-align': 'center'}), label='Email', max_length=60, required=True)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username[0].isupper() == False:
            raise  forms.ValidationError("Please enter a valid username with first letter in upper case")
        elif (username[1:] >= 'a' and username[1:] <= 'z') == False:
            raise forms.ValidationError("Please enter a valid username")
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            raise forms.ValidationError("Please enter a valid email address")

class UserUpdateForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter Name', 'text-align': 'center'}), label='Name', max_length=50, required=True)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username[0].isupper() == False:
            raise  forms.ValidationError("Please enter a valid username with first letter in upper case")
        elif (username[1:] >= 'a' and username[1:] <= 'z') == False:
            raise forms.ValidationError("Please enter a valid username")


class UserPasswordConfirmationForm(forms.Form):
    password=forms.CharField(widget=forms.PasswordInput(), label="Password", max_length=15, required=True)
    confirm_password=forms.CharField(widget=forms.PasswordInput(), label="Confirm Password", max_length=15, required=True)

    def clean(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise forms.ValidationError("Password and Confirm Password does not match")
        elif len(password) < 8 or len(password) > 15:
            raise forms.ValidationError("Password length mush not be less than 8 or greater than 15")
        elif not bool(re.search(r'[A-Z]', password)):
            raise forms.ValidationError("Password must have atleast one CAPS letter")
        elif not bool(re.search(r'\d', password)):
            raise forms.ValidationError("Password must have atleast one Number")
        elif not re.findall('[@_!#$%^&*()<>?/|}{~:]', password):
            raise forms.ValidationError("Password must have atleast one Special Character from the list:[?, !, @, #, ^, &, -, ~]")


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Enter Email', 'text-align': 'center'}), label='Email', max_length=60, required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter Password', 'text-align': 'center'}), label='Password', max_length=15, required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            raise forms.ValidationError("Please enter a valid email address")
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8 or len(password) > 15:
            raise forms.ValidationError("Password length mush not be less than 8 or greater than 15")
        elif not bool(re.search(r'[A-Z]', password)):
            raise forms.ValidationError("Password must have atleast one CAPS letter")
        elif not bool(re.search(r'\d', password)):
            raise forms.ValidationError("Password must have atleast one Number")
        elif not re.findall('[@_!#$%^&*()<>?/|}{~:]', password):
            raise forms.ValidationError("Password must have atleast one Special Character")
    
    
class ResetPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Enter Email', 'text-align': 'center'}), label='Email', max_length=60, required=True)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            raise forms.ValidationError("Please enter a valid email address")


class ResetPasswordConfirmForm(forms.Form):
    password=forms.CharField(widget=forms.PasswordInput(), label="New Password", max_length=15, required=True)
    confirm_password=forms.CharField(widget=forms.PasswordInput(), label="New Password Confirmation", max_length=15, required=True)

    def clean(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise forms.ValidationError("Password and Confirm Password does not match")
        elif len(password) < 8 or len(password) > 15:
            raise forms.ValidationError("Password length must not be less than 8 or greater than 15")
        elif not bool(re.search(r'[A-Z]', password)):
            raise forms.ValidationError("Password must have atleast one CAPS letter")
        elif not bool(re.search(r'\d', password)):
            raise forms.ValidationError("Password must have atleast one Number")
        elif not re.findall('[@_!#$%^&*()<>?/|}{~:]', password):
            raise forms.ValidationError("Password must have atleast one Special Character from the list:[?, !, @, #, ^, &, -, ~]")
