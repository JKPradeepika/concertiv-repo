from django.shortcuts import render
from django.views.generic import View
from django.db.models import Q
from .forms import *
from .models import *

from CPR.settings.dev import OSC_CLIENT_ID, OSC_CLIENT_SECRET

from pathlib import Path, PureWindowsPath
import os
import datetime
import jwt
import errno
import json
import csv
import shutil
import re
import pandas as pd

# Create your views here.
class BasicView(View):
    
     # Function to return config file path
    def config_path(self):
        cwd = os.getcwd()
        config_json_file_path = Path(os.path.join(cwd, "config.json"))
        with open(config_json_file_path) as f:
            data = json.load(f)
        return data
    
    # Function to return path of windows path of raw data file
    def base_path(self):
        data = self.config_path()
        username = os.getlogin()
        user_path = Path(os.path.join("C:/Users", username))
        elt_file_path = data["win_etl_output_files_path"]
        win_etl_file_path = Path(os.path.join(user_path, elt_file_path))
        return win_etl_file_path
    
    # Function to return path for oneschema - air
    def oneschema_hotels_path(self):
        username = os.getlogin()
        user_path = Path(os.path.join("C:/Users", username))
        data = self.config_path()
        oneschema_hotels_path = Path(os.path.join(user_path, data["oneschema_hotels_path"]))
        return oneschema_hotels_path
    
    def find_concertiv_ids(self, property_address):
        rs1, rs2, rs3 = [], [], []
        concertiv_ids_qs = Gds_codes.objects.values_list('concertiv_id', 'property_address')
        concertiv_ids = list(concertiv_ids_qs.values('concertiv_id', 'property_address'))
        for i in range(len(concertiv_ids)):
            concertiv_ids[i].update({'property_address': concertiv_ids[i]['property_address'].replace(concertiv_ids[i]['property_address'], concertiv_ids[i]['property_address'].title())})
        
        for ids in concertiv_ids:
            for k, v in ids.items():
                if k == 'property_address'and property_address in v:
                    rs1.append(ids)
        return rs1
                    
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
                        'domain': domain,
                        'travel_type': travel_type
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
    

class LoadRawDataView(BasicView):
    template_name = 'hotels/load_raw_data.html'
    error_url = 'commons/error.html'
        
    def post(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            osc_jwt_token = request.headers['Authorization']
            decode_jwt = jwt.decode(osc_jwt_token, OSC_CLIENT_SECRET, algorithms="HS256")
            if decode_jwt.get('iss') == OSC_CLIENT_ID:
                customer_name = decode_jwt.get('customer_name')
                quarter = decode_jwt.get('quarter')
                year = decode_jwt.get('year')
                country = decode_jwt.get('country')
                travel_agency = decode_jwt.get('travel_agency')
                domain = decode_jwt.get('domain')
                travel_type = decode_jwt.get('travel_type')
                payload = json.loads(request.body.decode('utf-8'))
                column_headers, template_key_headers = [], []
                for col in payload.get('columns'):
                    for k, v in col.items():
                        if k == "template_column_name":
                            column_headers.append(v)
                        elif k == "template_column_key":
                            template_key_headers.append(v)
                final_rec, rows = [], [] 
                for rec in payload.get('records'):
                    reordered_dict = {k: rec[k] for k in template_key_headers}
                    rows = list(reordered_dict.values())
                    final_rec.append(rows)
                one_schema_hotels_path = self.oneschema_hotels_path()
                final_oneschema_payload_path = PureWindowsPath(one_schema_hotels_path)
                csv_file_name = customer_name + "_" + travel_type + "_" + quarter + year + "_" + country + ".csv"
                csv_file_path = Path(os.path.join(final_oneschema_payload_path, csv_file_name))
                with open(csv_file_path, 'w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(column_headers)
                    csv_writer.writerows(final_rec)
                context = {'username': username, 'customer_name': customer_name, 'quarter': quarter, 'year': year, 'country': country, 'travel_agency': travel_agency, 'csv_file_path': csv_file_path}
                return render(request, self.template_name, context)   
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})
        return render(request, self.template_name, {'username': username})
    

class FuzzyMatchView(BasicView):
    template_name = 'hotels/final_rec.html'
    error_url = 'commons/error.html'
    
    def post(self, request, *args, **kwargs):
        # Reading CSV file
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            src_csv_file_path = request.POST.get('csv_file_path')
            customer_name = request.POST.get('customer_name')
            travel_agency = request.POST.get('travel_agency')
            country = request.POST.get('country')
            year = request.POST.get('year')
            quarter = request.POST.get('quarter')
            try:
                if os.path.exists(src_csv_file_path):
                    win_etl_file_path = self.base_path()
                    win_etl_output_file_path = Path(os.path.join(win_etl_file_path, customer_name))
                    dropbox_path = Path(os.path.join(win_etl_output_file_path, "3. Performance Reports", year, quarter, "Raw TMC Data-Dev"))
                    final_dropbox_path = PureWindowsPath(dropbox_path)
                    csv_file_name = customer_name + "_Hotels_" + quarter + year + "_" + country + ".csv"
                    dest_csv_file_path = Path(os.path.join(final_dropbox_path, csv_file_name))
                    shutil.copy(src_csv_file_path, dest_csv_file_path)
                    df = pd.read_csv(dest_csv_file_path)
                    
                    gds_codes_lst, df_fpa_lst, fp_lst, nfp_lst = [], [], [], []
                    gds_codes_qs = list(Gds_codes.objects.values('concertiv_id', 'property_address'))
                    
                    property_address = set(df["Property Address"].to_list())
                    property_address_lst = list(property_address)
                    for pa in property_address_lst:
                        pa = pa.upper()
                        for gd in gds_codes_qs:
                            for k, v in gd.items():
                                if k == 'property_address' and pa == v:
                                    fp_lst.append(gd)
                                else:
                                    nfp_lst.append(pa)
                                    for nfp in nfp_lst:
                                        npf = re.split(', | ,| | - ', nfp)
                                        print(npf)
                            
                    # print(fp_lst, ":", len(fp_lst))
                        # qs1 = Gds_codes.objects.filter(property_address__startswith=p[0]).values('concertiv_id', 'property_address')
                        # rs1.append(list(qs1.values('concertiv_id', 'property_address')))
                        # if (len(rs1) > 1) or (rs1 == []):
                        #     qs2 = qs1.filter(property_address__startswith=p[0]).filter(property_address__contains=p[1]).values('concertiv_id', 'property_address')
                        #     rs2.append(list(qs2.values_list('concertiv_id', 'property_address')))
                        #     if (len(rs2) > 1) or (rs2 == []):
                        #         qs3 = qs2.filter(property_address__contains=p[0]).filter(property_address__contains=p[1]).filter(property_address__contains=p[2]).values('concertiv_id', 'property_address')
                        #         rs3.append(list(qs3.values('concertiv_id', 'property_address')))
                        #         print(rs3)
                    
                    context = {'username': username, 'customer_name': customer_name, 'quarter': quarter, 'year': year, 'country': country}
                    return render(request, self.template_name, context=context)    
            except FileNotFoundError:
                message = ("Unable to find CSV file in specified directory: %s" % src_csv_file_path)
                context = {'message': message}
                return render(request, self.error_url, context)
