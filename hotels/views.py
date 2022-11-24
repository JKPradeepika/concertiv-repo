import csv
import datetime
import errno
import json
import operator
import os
import re
import shutil
from pathlib import Path, PureWindowsPath
from fuzzywuzzy import process
import time

import jwt
import pandas as pd
import numpy as np
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.shortcuts import render
from django.views.generic import View


from CPR.settings.dev import OSC_CLIENT_ID, OSC_CLIENT_SECRET

from .forms import HotelsRawdataForm
from .models import Gdscodes


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
    
    # Function to get concertiv_ids from fuzzy match output
    def get_concertiv_ids(self, element, concertiv_ids_lst):
        for i in concertiv_ids_lst:
            for k, v in i.items():
                if k == "property_address" and ((element in v) or (v in element) or (element == v)):
                    return i['concertiv_id']
        return None
    
    # Function to change date format for bo ctv discounts
    def change_date_format(self, bo_row_lst):
        final_bo_row_lst = []
        for bo in bo_row_lst:
            if type(bo) != str:
                continue
            else:
                bo = datetime.datetime.strptime(bo, "%Y-%m-%d")
                bo = datetime.datetime.strftime(bo, "%m/%d/%Y")
                final_bo_row_lst.append(bo)
        return final_bo_row_lst
    
    # Function to return ctv group dynamic discount list
    def find_ctv_grp_dynm_disc(self, bo_dates_list, fuzzy_ctv_ids_lst, fuzzy_checkin_dates_lst, group_ctv_df, group_bo_ctv_lst, bo_dates_dict):
        final_disc_lst, index_lst, n = [], [], 2
        start_date, end_date = "", ""
        group_ctv_lst = group_ctv_df['Concertiv_Hotel_UID'].tolist()
        for i, (j, k) in enumerate(zip(fuzzy_ctv_ids_lst, fuzzy_checkin_dates_lst)):
            if j in group_ctv_lst:
                disc = pd.Series(group_ctv_df.loc[group_ctv_df["Concertiv_Hotel_UID"] == j,  "Discount"]).to_list()
                final_disc_lst.append(disc)
                if j in group_bo_ctv_lst:
                    for k1, v in bo_dates_dict.items():
                        if k1 == j:
                            v = [bo_dates_dict[j][m * n:(j + 1) * n] for m in range((len(bo_dates_dict[j]) + n - 1) // n)]
                            for bo in v:
                                start_date = bo[0]
                                end_date = bo[1]
                                if start_date <= k <= end_date:
                                    index_lst.append(i)

            else:
                final_disc_lst.append(None)
        
        for i, (j, k) in enumerate(zip(fuzzy_ctv_ids_lst, fuzzy_checkin_dates_lst)):
            if j in group_ctv_lst and j in group_bo_ctv_lst:
                for bo in bo_dates_list:
                    start_date = bo[0]
                    end_date = bo[1]
                    if start_date <= k <= end_date:
                        for x in index_lst:
                            final_disc_lst[x] = None
            
        return final_disc_lst
                        
    
    # Function to read path :: Group Discount Mappings - Hotels file
    def read_group_mappings(self):
        csv_file_path_lst = []
        username = os.getlogin()
        user_path = Path(os.path.join("C:/Users", username))
        data = self.config_path()
        group_mapping_file_path = data["hotels_group_mapping_path"]
        group_mapping_file = Path(os.path.join(user_path, group_mapping_file_path))
        path = PureWindowsPath(group_mapping_file)
        full_file_path = Path(os.path.join(path, "Group Hotel Discounts Mapping.xlsx"))
        xl = pd.ExcelFile(full_file_path)
        for sheet in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet)
            csv_file_name = ''.join([str(sheet), ".csv"])
            csv_file_path = Path(os.path.join(path, csv_file_name))
            df.to_csv(csv_file_path, encoding='utf-8', index=False)
            csv_file_path_lst.append(str(csv_file_path))
        return csv_file_path_lst
                    
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
        travel_type = "Hotels"
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
                    print(e)
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
            decode_jwt = jwt.decode(osc_jwt_token, OSC_CLIENT_SECRET, algorithms=["HS256"])
            if decode_jwt.get('iss') == OSC_CLIENT_ID:
                customer_name = decode_jwt.get('customer_name')
                quarter = decode_jwt.get('quarter')
                year = decode_jwt.get('year')
                country = decode_jwt.get('country')
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
                csv_file_name = "{}_{}_{}{}_{}.csv".format(customer_name, travel_type, quarter, year, country)
                csv_file_path = Path(os.path.join(final_oneschema_payload_path, csv_file_name))
                with open(csv_file_path, 'w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(column_headers)
                    csv_writer.writerows(final_rec)
                context = {'username': username, 'customer_name': customer_name, 'quarter': quarter, 'year': year, 'country': country, 'travel_type': travel_type, 'csv_file_path': csv_file_path}
                return render(request, self.template_name, context)   
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})
        return render(request, self.template_name, {'username': username})
    

class FuzzyMatchView(BasicView):
    template_name = 'hotels/final_rec.html'
    error_url = 'commons/error.html'
    
    def post(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            src_csv_file_path = request.POST.get('csv_file_path')
            dest_csv_file_path = ""
            customer_name = request.POST.get('customer_name')
            request.session['customer_name'] = customer_name
            country = request.POST.get('country')
            request.session['country'] = country
            travel_type = request.POST.get('travel_type')
            request.session['travel_type'] = travel_type
            year = request.POST.get('year')
            request.session['year'] = year
            quarter = request.POST.get('quarter')
            request.session['quarter'] = quarter
            try:
                if os.path.exists(src_csv_file_path):
                    win_etl_file_path = self.base_path()
                    win_etl_output_file_path = Path(os.path.join(win_etl_file_path, customer_name))
                    dropbox_path = Path(os.path.join(win_etl_output_file_path, "3. Performance Reports", year, quarter, "Raw TMC Data-Dev"))
                    final_dropbox_path = PureWindowsPath(dropbox_path)
                    csv_file_name = "{}_{}_{}{}_{}.csv".format(customer_name, travel_type, quarter, year, country)
                    dest_csv_file_path = Path(os.path.join(final_dropbox_path, csv_file_name))
                    
                    # Copying .CSV file from the oneschema directory to the destination folder
                    shutil.copy(src_csv_file_path, dest_csv_file_path)
                    
                    # Converting .CSV file to dataframe
                    df = pd.read_csv(dest_csv_file_path)
                    
                    converted_data, rs, nrs = [], [], []
                    property_address_lst = df["Property Address"].to_list()
                    
                    initial_time = time.time()
                    # New Fuzzy Match logic
                    new_property_address_lst = list()
                    for pa in property_address_lst:
                        pa = pa.upper()
                        new_property_address_lst.append(pa)
                    new_qs = Gdscodes.objects.values('concertiv_id', 'property_address')
                    res = np.array(new_qs)
                    new_ctv_ids_lst, final_lst, other_final_lst, ids_lst = list(), list(), list(), list()
                    for npa in new_property_address_lst:
                        for r in res:
                            for k, v in r.items():
                                if k == 'property_address' and npa.__contains__(v):
                                    new_ctv_ids_lst.append(r)
                    print(new_ctv_ids_lst, ":", len(new_ctv_ids_lst))
                    
                    for i, npa in enumerate(new_property_address_lst):
                        for n in new_ctv_ids_lst:
                            for k, v in n.items():
                                if k == 'property_address' and npa.__contains__(v):
                                    final_lst.append(n['concertiv_id'])
                                    del new_property_address_lst[i]
                                else:
                                    other_final_lst.append(process.extractOne(npa, new_property_address_lst))
                                    # ids_lst = list(map(operator.itemgetter(0), other_final_lst))
                                    
                    print("other_final_lst",other_final_lst, ":", len(other_final_lst)) 
                    print(new_property_address_lst, ":", len(new_property_address_lst)) 
                    # new_property_address_st_lst = np.array(set(new_property_address_lst))
                    # other_final_lst = [process.extractOne(x, new_property_address_st_lst) for x in new_property_address_lst]
                    # ids_lst = list(map(operator.itemgetter(0), other_final_lst))
                    # print(ids_lst, ":", len(ids_lst))
                    # final_lst.extend(ids_lst)
                    print("after process.extractOne:", final_lst, ":", len(final_lst))
                    print(time.time() - initial_time)
                    # Fuzzy Match logic
                    # for pa in property_address_lst:
                    #     pa = pa.upper()
                    #     qs = Gdscodes.objects.filter(property_address__icontains=pa).values('concertiv_id', 'property_address')
                    #     if len(qs) == 1:
                    #         rs.append(list(qs))
                    #     else:
                    #         pa = re.split(", | | - |'", pa)
                    #         converted_data.append(pa)
                            
                    # for i in converted_data:
                    #     qs1 = Gdscodes.objects.annotate(search=SearchVector('property_address')).filter(search=SearchQuery(i[0])).values('concertiv_id', 'property_address')
                    #     if len(qs1) == 1:
                    #         rs.append(list(qs1))
                    #     else:
                    #         qs2 = qs1.filter(search=SearchQuery(i[0]) & SearchQuery(i[1])).values('concertiv_id', 'property_address')
                    #         if len(qs2) == 1:
                    #             rs.append(list(qs2))
                    #         elif len(i) == 2:
                    #             qs3 = qs2.filter(search=SearchQuery(i[0]) & SearchQuery(i[1])).values('concertiv_id', 'property_address')
                    #             rs.append(list(qs3))
                    #             if len(rs) == len(property_address_lst):
                    #                 break
                    #         else:
                    #             qs4 = Gdscodes.objects.annotate(search=SearchVector('property_address')).filter(search=SearchQuery(i[0]) & SearchQuery(i[2])).values('concertiv_id', 'property_address')
                    #             if len(qs4) == 1:
                    #                 rs.append(list(qs4))
                    #                 if len(rs) == len(property_address_lst):
                    #                     break
                    #             else:
                    #                 nrs.append(i)
                                    
                    # concertiv_ids, ids_lst, final_ids_lst = [], [], []
                    # df_property_address_lst = df['Property Address'].to_list()
                    
                    # # Extracting best option from Fuzzy Match
                    # [concertiv_ids.append(s) for r in rs if len(r) == 1 for s in r]
                    # concertiv_ids_tmp = [process.extractOne(i, concertiv_ids) for i in df_property_address_lst]
                    # ids_lst = list(map(operator.itemgetter(0), concertiv_ids_tmp))
                    # print(ids_lst, ":", len(ids_lst))
                    # [final_ids_lst.append(self.get_concertiv_ids(i, ids_lst)) for i in df_property_address_lst]
                    
                    # Insert concertiv_ids into dataframe
                    # df.insert(8, "Concertiv ID", [i for i in final_lst])
                    
                    # Adding new column - concertiv_id into excel sheet
                    new_file_name = "{}_{}_{}{}_{}_FuzzyMatch.xlsx".format(customer_name, travel_type, quarter, year, country)
                    new_file_path = Path(os.path.join(final_dropbox_path, new_file_name))
                    # request.session["fuzzy_match_file"] = new_file_path
                    df.to_excel(new_file_path, index=False)
                    context = {'username': username, 'customer_name': customer_name, 'quarter': quarter, 'year': year, 'country': country, "file_path": new_file_path}
                    return render(request, self.template_name, context=context)    
            except FileNotFoundError:
                message = ("Unable to find CSV file in specified directory: %s" % src_csv_file_path)
                context = {'message': message}
                return render(request, self.error_url, context)
            finally:
                # Deleting previous version of CSV
                if os.path.exists(dest_csv_file_path):
                    os.remove(dest_csv_file_path)
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})
                    

class CTVGroupSavingsCalculation(BasicView):
    template_name = 'hotels/savings_calculation.html'
    success_url = 'hotels/final_rec.html'
    error_url = 'commons/error.html'     
    
    def get(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            request.session['customer_name'] = "Freepoint"
            request.session['quarter'] = "Q3"
            request.session['year'] = "2022"
            request.session['country'] = "US"
            request.session['travel_type'] = "CTM"
            return render(request, self.template_name, context={'username': username})
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message}) 
        
    def post(self, request, *args, **kwargs):
        if request.session.has_key('username'):
            username = request.session.get('username')
            request.session.modified = True
            uploaded_file = request.FILES['fuzzy_match_document']
            uploaded_file_name = uploaded_file.name
            customer_name = request.session.get('customer_name')
            travel_type = request.session.get('travel_type')
            quarter = request.session.get('quarter')
            year = request.session.get('year')
            country = request.session.get('country')
            
            
            # Reading from the .csv files - Group CTV ID and Group - BO dates
            csv_file_paths_lst = list()
            win_etl_file_path = self.base_path()
            win_etl_output_file_path = Path(os.path.join(win_etl_file_path, customer_name))
            dropbox_path = Path(os.path.join(win_etl_output_file_path, "3. Performance Reports", year, quarter, "Raw TMC Data-Dev"))
            final_dropbox_path = PureWindowsPath(dropbox_path)
            csv_file_name = customer_name + "_" + travel_type + "_" +quarter + year + "_" + country + ".csv"
            csv_file = Path(os.path.join(final_dropbox_path, csv_file_name))
            excel_file = Path(os.path.join(final_dropbox_path, uploaded_file_name))
            
            try:
                if os.path.exists(excel_file):
                    # Reading .csv file and converting into dataframe object
                    csv_file_paths_lst = self.read_group_mappings()
                    fuzzy_excel_df = pd.read_excel(excel_file)
                    fuzzy_excel_df.to_csv(csv_file)
                    fuzzy_df = pd.read_csv(csv_file)
                    group_ctv_df = pd.read_csv(csv_file_paths_lst[0])
                    group_bo_df = pd.read_csv(csv_file_paths_lst[1])
                    
                    # Extracting BO dates and concertiv id in dictionary
                    group_bo_ctv_lst = group_bo_df['CTV ID'].tolist()
                    bo_rows_lst = []
                    for index, rows in group_bo_df.iterrows():
                        row_lst = [rows.BO1_s, rows.BO1_e, rows.BO2_s, rows.BO2_e, rows.BO3_s, rows.BO3_e, rows.BO4_s, rows.BO4_e, rows.BO5_s, rows.BO5_e,
                                    rows.BO6_s, rows.BO6_e, rows.BO7_s, rows.BO7_e, rows.BO8_s, rows.BO8_e, rows.BO9_s, rows.BO9_e, rows.BO10_s, rows.BO10_e]
                        row_lst = self.change_date_format(row_lst)
                        bo_rows_lst.append(row_lst)
                    bo_dates_dict = dict()
                    for ctv_id, bo_dates in zip(group_bo_ctv_lst, bo_rows_lst):
                        bo_dates_dict[ctv_id] = bo_dates
                    
                    # Extracting Group Discounts - Dynamic
                    fuzzy_checkin_dates_lst, bo_dates_lst, group_dynmc_disc_lst = [], [], []
                    fuzzy_ctv_ids_lst = fuzzy_df['concertiv_uid'].tolist()
                    fuzzy_df['checkin_date'] = pd.to_datetime(fuzzy_df['checkin_date'], format="%Y-%m-%d")
                    fuzzy_df['checkin_date'] = pd.to_datetime(fuzzy_df['checkin_date']).dt.strftime("%m/%d/%Y")
                    fuzzy_df['checkout_date'] = pd.to_datetime(fuzzy_df['checkout_date'], format="%Y-%m-%d")
                    fuzzy_df['checkout_date'] = pd.to_datetime(fuzzy_df['checkout_date']).dt.strftime("%m/%d/%Y")
                    fuzzy_df['spend'] = fuzzy_df['spend'].round(decimals=2)
                    fuzzy_checkin_dates_lst = fuzzy_df['checkin_date'].tolist()
                    n = 2
                    for i in fuzzy_ctv_ids_lst:
                        if i in bo_dates_dict.keys():
                            bo_dates_lst = [bo_dates_dict[i][j * n:(j + 1) * n] for j in range((len(bo_dates_dict[i]) + n - 1) // n)]
                    disc_lst = self.find_ctv_grp_dynm_disc(bo_dates_lst, fuzzy_ctv_ids_lst, fuzzy_checkin_dates_lst, group_ctv_df, group_bo_ctv_lst, bo_dates_dict)
                    for d in disc_lst:
                        if d == None:
                            group_dynmc_disc_lst.append(None)
                        else:
                            for j in d:
                                group_dynmc_disc_lst.append(j)
                    print(group_dynmc_disc_lst, ":", len(group_dynmc_disc_lst))
                    print("original length of dataframe from fuzzy match:", len(fuzzy_checkin_dates_lst))
                                
                    # Insert concertiv_ids into dataframe
                    del fuzzy_df['Unnamed: 0']
                    fuzzy_df.insert(10, "Group Discount - Dynamic", [i for i in group_dynmc_disc_lst])

                    new_file_name = "{}_{}_{}{}_{}_FinalData.xlsx".format(customer_name, travel_type, quarter, year, country)
                    new_file_path = Path(os.path.join(final_dropbox_path, new_file_name))
                    fuzzy_df.to_excel(new_file_path, index=False)
                    context = {'username': username, 'file_path': new_file_path}
                    return render(request, self.success_url, context=context)
            except FileExistsError:
                message = ("Unable to find excel file in specified directory: %s" % excel_file)
                context = {'message': message}
                return render(request, self.error_url, context)
            finally:
                for csv_path in csv_file_paths_lst:
                    if os.path.exists(csv_path):
                        os.remove(csv_path)
                if os.path.exists(csv_file):
                    os.remove(csv_file)
        else:
            message = "Unauthorized access. Please login again."
            return render(request, self.error_url, context={'message': message})

