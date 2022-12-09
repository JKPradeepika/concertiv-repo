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
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'password', 'text-align': 'center'}), label='Password', max_length=15, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'confirm password', 'text-align': 'center'}), label=' Confirm Password', max_length=15, required=True)
    
    def clean_passwords(self):
        special_characters = ['?', '!', '@', '#', '^', '&', '-', '~']
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if len(password) < 8 or len(password) > 15:
            raise forms.ValidationError("Password length mush not be less than 8 or greater than 15")
        else:
            for i in password:
                if i.isdigit() == False:
                    raise forms.ValidationError("Please ensure to have atleast one number in the password")
                elif i.isupper() == False:
                    raise forms.ValidationError("Please ensure to have atleast one CAPS in the password")
                elif i not in special_characters:
                    raise forms.ValidationError("Please ensure to have atleast one special character from the list:[?, !, @, #, ^, &, -, ~] in the password")
        
        if password != confirm_password:
            raise forms.ValidationError("Password and Confirm Password does not match")
        
                