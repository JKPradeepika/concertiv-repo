from django import forms

CLIENT_NAMES = [('', 'Enter client name'),
                ('American Securities','American Securities'),
                ('BakerHostetler', 'BakerHostetler'),
                ('PWP','PWP'),
                ('CD&R', 'CD&R')]

QUARTERS = [('', 'Enter quarter'), ('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q4', 'Q4')]

class HotelsRawdataForm(forms.Form):
    travel_agency = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter travel agency', 'text-align': 'center'}), label='Agency', max_length=50, required=True)
    customer_name = forms.CharField(widget=forms.Select(choices=CLIENT_NAMES, attrs={'class':'form-control form-control-sm', 'text-align': 'center'}), label='Client Name', max_length=50, required=True)
    country = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter country', 'text-align': 'center'}), label='Country', max_length=2, required=True)
    quarter = forms.CharField(widget=forms.Select(choices=QUARTERS, attrs={'class':'form-control form-control-sm', 'text-align': 'center'}), label='Quarter', max_length=2, required=True)
    year = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder':'Enter year', 'text-align': 'center'}), label='Year', max_length=4, required=True)
    
    def clean_customer_name(self):
        customer_name = self.cleaned_data.get("customer_name")
        if customer_name == None:
                raise forms.ValidationError("Please select a valid customer name.")
        return customer_name
    
    def clean_travel_agency(self):
        travel_agency = self.cleaned_data.get("travel_agency")
        if travel_agency.isalpha() == False:
            raise forms.ValidationError("Only alphabets are allowed. Please enter a valid travel agency.")
        return travel_agency
    
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
