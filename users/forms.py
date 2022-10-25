from django import forms
import re

class AdminLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter Username', 'text-align': 'center'}), label='Username', max_length=50, required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter Password', 'text-align': 'center'}), label='Password', max_length=10, required=True)
    

class UserSignupForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter Username', 'text-align': 'center'}), label='Username', max_length=50, required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Enter Email', 'text-align': 'center'}), label='Email', max_length=256, required=True)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username[0].isupper() == False:
            raise  forms.ValidationError("Please enter a valid username with first letter in upper case")
        elif (username[1:] >= 'a' and username[1:] <= 'z') == False:
            raise forms.ValidationError("Please enter a valid username")
    
    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w[a-z]+[.]\w{2,3}$'
    #     if not re.search(regex, email):
    #         raise forms.ValidationError("Please enter a valid email address")
    