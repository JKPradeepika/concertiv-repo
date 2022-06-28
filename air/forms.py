from django import forms

class RawdataForm(forms.Form):
    customer_name = forms.CharField(widget=forms.TextInput, label='Enter Customer Name', max_length=100, required=True)
    travel_agency = forms.CharField(widget=forms.TextInput, label='Enter Travel Agency', max_length=100, required=True)
    year = forms.CharField(widget=forms.TextInput, label='Enter Year', max_length=4, required=True)
    quarter = forms.CharField(widget=forms.TextInput, label='Enter Quarter', max_length=2, required=True)
    country = forms.CharField(widget=forms.TextInput, label='Enter Country', max_length=2, required=True)
    
