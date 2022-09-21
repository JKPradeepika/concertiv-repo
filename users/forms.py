from django import forms

class AdminLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter Username', 'text-align': 'center'}), label='Username', max_length=50, required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter Password', 'text-align': 'center'}), label='Password', max_length=10, required=True)