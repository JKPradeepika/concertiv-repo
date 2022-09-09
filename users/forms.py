from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'enter first name', 'text-align': 'center'}), label='First Name', max_length=30, required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'enter last name', 'text-align': 'center'}), label='Last Name', max_length=30, required=True)
    employee_id = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'enter employee id', 'text-align': 'center'}), label='Employee Id', max_length=5, required=True)
    company_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'enter company name', 'text-align': 'center'}), label='Company Name', max_length=15, required=True)
    team_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'enter team name', 'text-align': 'center'}), label='Team Name', max_length=15, required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control form-control-sm', 'placeholder':'enter email', 'text-align': 'center'}), label='Email', max_length=254, required=True)

    class Meta:
        model = User
        fields = [
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'password1', 
            'password2', 
            ]