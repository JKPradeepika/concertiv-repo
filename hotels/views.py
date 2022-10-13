from django.shortcuts import render
from django.views.generic import View

from .forms import *

from CPR.settings.dev import OSC_CLIENT_ID, OSC_CLIENT_SECRET

import datetime
import jwt
import errno


# Create your views here.
class RawDataView(View):
    form_class = HotelsRawdataForm
    template_name = 'hotels/raw_data.html'
    success_url = 'hotels/get_raw_data.html'
    error_url = 'commons/error.html'
    
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
        domain = "travel"
        travel_type = "hotels"
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            try:
                if form.is_valid():
                    customer_name = request.POST.get('customer_name')
                    travel_agency = request.POST.get('travel_agency')
                    quarter = request.POST.get('quarter')
                    year = request.POST.get('year')
                    country = request.POST.get('country')
                    data = {
                        'iss': OSC_CLIENT_ID,
                        'exp': datetime.datetime.now() + datetime.timedelta(minutes=15),
                        'username': username,
                        'customer_name': customer_name, 
                        'quarter': quarter, 
                        'year': year,
                        'travel_agency': travel_agency,
                        'country': country,
                    }
                    encode_jwt = jwt.encode(payload = data, key=OSC_CLIENT_SECRET, algorithm='HS256')
                    context = {'username': username, 'customer_name': customer_name, 'quarter': quarter, 'year': year, 'country': country, 'travel_agency': travel_agency, 'encode_jwt': encode_jwt, 'domain': domain, 'travel_type': travel_type }
                    return render(request, self.success_url, context)
                else:
                    form = self.form_class(request.POST)
            except IOError as e:
                if e.errno == errno.EPIPE:
                    pass
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})
        return render(request, self.template_name, context={'form': form, 'username': username})