from django import forms

class AdminLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter Username', 'text-align': 'center'}), label='Username', max_length=50, required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter Password', 'text-align': 'center'}), label='Password', max_length=10, required=True)
    

class UserSignupForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter Firstname', 'text-align': 'center'}), label='First Name', max_length=50, required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter Lastname', 'text-align': 'center'}), label='Last Name', max_length=50, required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Enter Email', 'text-align': 'center'}), label='Email', max_length=256, required=True)
    is_superuser = forms.BooleanField(label="Superuser?")
    
    