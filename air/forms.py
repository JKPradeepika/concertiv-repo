from django import forms
from .models import Preference


class RawdataForm(forms.Form):
    customer_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'enter client name', 'text-align': 'center'}), label='Client Name', max_length=100, required=True)
    year = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'enter year', 'text-align': 'center'}), label='Year', max_length=4, required=True)
    quarter = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'enter quarter', 'text-align': 'center'}), label='Quarter', max_length=2, required=True)
    country = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'enter country', 'text-align': 'center'}), label='Country', max_length=2, required=True)

    def clean_customer_name(self):
        customer_name = self.cleaned_data.get("customer_name")
        for i in range(len(customer_name)):
            if ((customer_name[i] >= 'A' and customer_name[i] <= 'Z') or (customer_name[i] >= 'a' and customer_name[i] <= 'z') or customer_name[i] == "&") == False:
                raise forms.ValidationError("Only alphabets are allowed. Please enter a valid customer name.")
        return customer_name
    
    def clean_year(self):
        year = self.cleaned_data.get("year")
        if not year:
            raise forms.ValidationError("Year cannot be empty.")
        elif year.isnumeric() == False:
            raise forms.ValidationError("Only numbers are allowed. Please enter a valid year.")
        return year
    
    def clean_quarter(self):
        quarter = self.cleaned_data.get("quarter")
        if quarter.isalnum() == False:
            raise forms.ValidationError("Only alphabets and numbers are allowed. Please enter a valid quarter.")
        return quarter
    
    def clean_country(self):
        country = self.cleaned_data.get("country")
        if country.isupper() == False:
            raise forms.ValidationError("Only upper case alphabets are allowed. Please enter a valid country.")
        return country
