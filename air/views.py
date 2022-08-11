from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView, View
from matplotlib.pyplot import axis
from pyparsing import col
from .forms import *
from .models import *

from pathlib import Path, PureWindowsPath
from django.db import connection
import os
import json
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

    # Function which returns Year Half based on Quarter
    def half_year(self, quarter):
        if quarter == "Q1" or quarter == "Q2":
            return "H1"
        else:
            return "H2"

    # Function which returns contract classifier for all Prism flights
    def savings_classifier(self, classifier_names, jet_departure_date, jet_booking_class_code, emi_references, tur_references, qan_references, sin_references):
        jet_ctv_references, emi_ctv_references, tur_ctv_references, qan_ctv_references, sin_ctv_references, jet_indexes, emi_indexes, tur_indexes, qan_indexes, sin_indexes = [], [], [], [], [], [], [], [], [], []
        data = self.config_path()
        for cn in range(len(classifier_names)):
            if classifier_names[cn] == "JetBlue":
                jet_indexes.append(cn)
            elif classifier_names[cn] == "Emirates":
                emi_indexes.append(cn)
            elif classifier_names[cn] == "Turkish":
                tur_indexes.append(cn)
            elif classifier_names[cn] == "Qantas":
                qan_indexes.append(cn)
            elif classifier_names[cn] == "Singapore":
                sin_indexes.append(cn)
        for jd in range(len(jet_departure_date)):
            dd = data["jet_departure_date"]
            [jet_ctv_references.append(''.join("Pre May 2019" + "-" + bc)) if jet_departure_date[jd] <= dd else jet_ctv_references.append(''.join("Post May 2019" + "-" + bc)) for bc in jet_booking_class_code[jd]]
        [emi_ctv_references.append(e) for e in emi_references]
        [tur_ctv_references.append(t) for t in tur_references]
        [qan_ctv_references.append(q) for q in qan_references]
        [sin_ctv_references.append(s) for s in sin_references]
        return jet_ctv_references, emi_ctv_references, tur_ctv_references, qan_ctv_references, sin_ctv_references, jet_indexes, emi_indexes, tur_indexes, qan_indexes, sin_indexes

    # Function to return tour code and ticket designator for all Prism airlines based on savings contract classifier
    def tour_code_and_ticket_designator(self):
        data = self.config_path()
        for k, v in data["tour_code_and_ticket_designator"].items():
            if k == "JetBlue":
                for k1, v1 in v.items():
                    jet_tour_code = v["jet_tour_code"]
                    jet_ticket_designator = v["jet_ticket_designator"]
            elif k == "Emirates":
                for k1, v1 in v.items():
                    emi_tour_code = v["emi_tour_code"]
                    emi_ticket_designator = v["emi_ticket_designator"]
            elif k == "Turkish":
                for k1, v1 in v.items():
                    tur_tour_code = v["tur_tour_code"]
                    tur_ticket_designator = v["tur_ticket_designator"]
            elif k == "Qantas":
                for k1, v1 in v.items():
                    qan_tour_code = v["qan_tour_code"]
            elif k == "Singapore":
                for k1, v1 in v.items():
                    sin_tour_code = v["sin_tour_code"]
                    sin_ticket_designator = v["sin_ticket_designator"]
        return jet_tour_code, jet_ticket_designator, emi_tour_code, emi_ticket_designator, tur_tour_code, tur_ticket_designator, qan_tour_code, sin_tour_code, sin_ticket_designator

    # Function to read Group Mappings for Preferred Savings Classifiers
    def read_group_mappings(self, customer_name, quarter, year):
        win_etl_file_path = self.base_path()
        win_etl_output_file_path = Path(os.path.join(win_etl_file_path, customer_name))
        reports_path = Path(os.path.join(win_etl_output_file_path, "3. Performance Reports", year, quarter, "Raw TMC Data-Dev"))
        path = PureWindowsPath(reports_path)
        full_file_path = Path(os.path.join(path, "Group Airline Discounts Mapping.xlsx"))
        csv_file_path = Path(os.path.join(path, "Group Airline Discounts Mapping.csv"))
        xl = pd.ExcelFile(full_file_path)
        df = pd.read_excel(xl, sheet_name=None)
        df = pd.concat(df, ignore_index=True)
        df.to_csv(csv_file_path, encoding='utf8', index=False)
        df = pd.read_csv(csv_file_path)
        return df

    # Function to assign discount based on reference_list
    def assign_discount(self, discount, discount_reference_list, indices_list, reference_list, df):
        loc_list = []
        for tk in discount_reference_list:
            if tk in reference_list:
                index = int(df[df["Reference"] == tk].index[0])
                loc = df.at[index, "Discount"]
                loc_list.append(loc)
            else:
                missing_value = 99999.9
                loc_list.append(missing_value)
        p = dict(zip(indices_list, loc_list))
        m = list(p.values())
        j = list(p.keys())
        for i in range(len(discount)):
            for k in range(len(j)):
                if i == j[k]:
                    discount[i] = m[k]
        return discount

    # Function to check whether the tour code and ticket designator are available or not to determine discount
    def check_tour_code_and_ticket_designator(self, df, discount, savings_tour_code, savings_ticket_designator, customer_name, quarter, year, index_list, tour_code, ticket_designator):
        group = self.read_group_mappings(customer_name, quarter, year)
        reference_list = group["Reference"].tolist()
        discount_contract_classifier = df["Savings Contract Classifier"].tolist()
        discount_reference_list, indices_list = [], []
        for i in range(len(index_list)):
            if df["Tour Code"].iloc[index_list[i]] == "nan" and df["Ticket Designator"].iloc[index_list[i]] == ticket_designator:
                discount_reference_list.append(discount_contract_classifier[index_list[i]])
                indices_list.append(index_list[i])
                savings_tour_code[index_list[i]] = "Not Available, Not Matched"
                savings_ticket_designator[index_list[i]] = "Available, Matched"
                self.assign_discount(discount, discount_reference_list, indices_list, reference_list, group)
            elif df["Tour Code"].iloc[index_list[i]] == tour_code and df["Ticket Designator"].iloc[index_list[i]] == "nan":
                discount_reference_list.append(discount_contract_classifier[index_list[i]])
                indices_list.append(index_list[i])
                savings_tour_code[index_list[i]] = "Available, Matched"
                savings_ticket_designator[index_list[i]] = "Not Available, Not Matched"
                self.assign_discount(discount, discount_reference_list, indices_list, reference_list, group)
            elif df["Tour Code"].iloc[index_list[i]] == tour_code and df["Ticket Designator"].iloc[index_list[i]] != "nan":
                discount_reference_list.append(discount_contract_classifier[index_list[i]])
                indices_list.append(index_list[i])
                savings_tour_code[index_list[i]] = "Available, Matched"
                if df["Ticket Designator"].iloc[index_list[i]] != ticket_designator:
                    savings_ticket_designator[index_list[i]] = "Available, Not Matched - " + df["Ticket Designator"].iloc[index_list[i]]
                else:
                    savings_ticket_designator[index_list[i]] = "Available, Matched"
                self.assign_discount(discount, discount_reference_list, indices_list, reference_list, group)
            elif df["Tour Code"].iloc[index_list[i]] != "nan" and df["Ticket Designator"].iloc[index_list[i]] == ticket_designator:
                discount_reference_list.append(discount_contract_classifier[index_list[i]])
                indices_list.append(index_list[i])
                if df["Tour Code"].iloc[index_list[i]] != tour_code:
                    savings_tour_code[index_list[i]] = "Available, Not Matched - " + df["Tour Code"].iloc[index_list[i]]
                else:
                    savings_tour_code[index_list[i]] = "Available, Matched"
                savings_ticket_designator[index_list[i]] = "Available, Matched"
                self.assign_discount(discount, discount_reference_list, indices_list, reference_list, group)
            elif df["Tour Code"].iloc[index_list[i]] == "nan" and df["Ticket Designator"].iloc[index_list[i]] == "nan":
                savings_tour_code[index_list[i]] = "Not Available, Not Matched"
                savings_ticket_designator[index_list[i]] = "Not Available, Not Matched"
            elif df["Tour Code"].iloc[index_list[i]] == "nan" and df["Ticket Designator"].iloc[index_list[i]] != ticket_designator:
                savings_tour_code[index_list[i]] = "Not Available, Not Matched"
                savings_ticket_designator[index_list[i]] = "Available, Not Matched - " + df["Ticket Designator"].iloc[index_list[i]]
            elif df["Tour Code"].iloc[index_list[i]] != tour_code and df["Ticket Designator"].iloc[index_list[i]] == "nan":
                savings_tour_code[index_list[i]] = "Available, Not Matched - " + df["Tour Code"].iloc[index_list[i]]
                savings_ticket_designator[index_list[i]] = "Not Available, Not Matched"
            elif df["Tour Code"].iloc[index_list[i]] != tour_code and df["Ticket Designator"].iloc[index_list[i]] == ticket_designator:
                savings_tour_code[index_list[i]] = "Not Available, Not Matched"
                savings_ticket_designator[index_list[i]] = "Not Available, Not Matched"
            elif df["Tour Code"].iloc[index_list[i]] != tour_code and df["Ticket Designator"].iloc[index_list[i]] != ticket_designator:
                savings_tour_code[index_list[i]] = "Available, Not Matched - " + df["Tour Code"].iloc[index_list[i]]
                savings_ticket_designator[index_list[i]] = "Available, Not Matched - " + df["Ticket Designator"].iloc[index_list[i]]
        return discount, savings_tour_code, savings_ticket_designator

    # Function returns discount, pre-discount and savings for Prism flights
    def prism_flights_info(self, file_path, csv_file_path, quarter_year, prism_airlines):
        prism_discount_list = []
        xl = pd.ExcelFile(file_path)
        df = pd.read_excel(xl, sheet_name="Air - PRISM & Other")
        df.to_csv(csv_file_path, encoding='utf8', index=False)
        df = pd.read_csv(csv_file_path)
        index_list = df.index[df["Quarter"] == quarter_year].tolist()
        for i, p in zip(index_list, prism_airlines):
            prism_discount_list.append(p)
            pre_discount = df.iloc[i]["Pre-Discount"]
            pre_discount = pre_discount.round(2)
            prism_discount_list.append(pre_discount)
            actual_spend = df.iloc[i]["Actual Spend"]
            actual_spend = actual_spend.round(2)
            prism_discount_list.append(actual_spend)
            savings = df.iloc[i]["Savings"]
            savings = savings.round(2)
            prism_discount_list.append(savings)
        return prism_discount_list

    # Function to calculate the total Pre discount, Savings and Fare
    def calculate_total(self, df, airline_list, airline_indexes, airline_pre_discount, airline_fare, airline_savings, total_prism_pre_discount, total_prism_actual_spend, total_prism_vol, total_prism_savings, total_prism_net):
        total_non_prism_pre_discount, total_non_prism_actual_spend, total_non_prism_vol, total_non_prism_savings, total_non_prism_net, total_non_prism_final_savings = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        total_non_prism_pre_discount = total_prism_pre_discount + airline_pre_discount
        pre_discount = "$" + "{:,.2f}".format(airline_pre_discount)
        airline_list.append(pre_discount)
        total_non_prism_actual_spend = total_prism_actual_spend + airline_fare
        fare = "$" + "{:,.2f}".format(airline_fare)
        airline_list.append(fare)
        vol = len(airline_indexes) / len(df.index)
        vol = (vol * 100)
        total_non_prism_vol = total_prism_vol + vol
        vol = "{:,.2f}".format(vol) + "%"
        airline_list.append(vol)
        total_non_prism_savings = total_prism_savings + airline_savings
        savings = "$" + "{:,.2f}".format(airline_savings)
        airline_list.append(savings)
        net = (airline_savings / airline_pre_discount) * 100
        total_non_prism_net = total_prism_net + net
        net = "{:,.2f}".format(net) + "%"
        airline_list.append(net)
        sum_savings = df["Savings"].sum()
        total_non_prism_final_savings = total_prism_savings + sum_savings * 2
        savings = "$" + "{:,.2f}".format(sum_savings)
        airline_list.append(savings)
        return airline_list, total_non_prism_pre_discount, total_non_prism_actual_spend, total_non_prism_vol, total_non_prism_savings, total_non_prism_net, total_non_prism_final_savings

class HomeView(TemplateView):
    template_name = 'air/home.html'

class RawDataView(BasicView):
    form_class = RawdataForm
    template_name = 'air/raw_data.html'
    success_url = 'air/get_raw_data.html'
    error_url = 'air/error.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        customer_name = request.POST.get('customer_name')
        request.session['customer_name'] = customer_name
        travel_agency = request.POST.get('travel_agency')
        request.session['travel_agency'] = travel_agency
        quarter = request.POST.get('quarter')
        request.session['quarter'] = quarter
        year = request.POST.get('year')
        request.session['year'] = year
        country = request.POST.get('country')
        request.session['country'] = country

        if form.is_valid():
            win_etl_file_path = self.base_path()
            win_etl_output_file_path = Path(os.path.join(win_etl_file_path, request.POST.get("customer_name")))
            reports_path = Path(os.path.join(win_etl_output_file_path, "3. Performance Reports", year, quarter, "Raw TMC Data-Dev"))
            path = PureWindowsPath(reports_path)
            file_path = ''
            for file_name in os.listdir(path):
                if not file_name.startswith(customer_name):
                    pass
                elif file_name.startswith(customer_name) and file_name.__contains__("Air") and file_name.__contains__(quarter) and file_name.__contains__(year) and file_name.__contains__(country) and file_name.__contains__(".xlsx"):
                    file_path = os.path.join(path, file_name)
                    csv_file = customer_name + "_Air_" + quarter + year + "_" + country + ".csv"
                    csv_file_path = os.path.join(path, csv_file)
                    request.session['csv_file_path'] = csv_file_path
            try:
                message = ""
                if os.path.exists(file_path):
                    message = "Found the file. Process the data..."
                    xl = pd.ExcelFile(file_path)
                    for sheet in xl.sheet_names:
                        df = pd.read_excel(xl, sheet_name=sheet)
                        df.to_csv(csv_file_path, encoding='utf8', index=False)
            except FileNotFoundError:
                message = "File not found. Please check the path and Try again."
                context = {'message': message}
                return render(request, self.error_url, context)
            context = {'customer_name': customer_name, 'quarter': quarter, 'year': year, 'file_path': file_path, 'message': message}
            return render(request, self.success_url, context)
        else:
            form = self.form_class(request.POST)
        return render(request, self.template_name, {'form': form})

class SuccessView(TemplateView):
    template_name = 'air/success.html'
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('success', args=request))

class ProcessDataView(BasicView):
    template_name = 'air/process_data.html'
    error_url = 'air/error.html'

    def post(self, request, *args, **kwargs):
        cwd = os.getcwd()
        csv_file_path = request.session['csv_file_path']
        customer_name = request.session['customer_name']
        year = request.session['year']
        quarter = request.session['quarter']
        travel_agency = request.session['travel_agency']
        country = request.session['country']

        # Reading CSV file
        try:
            new_file_path = ""
            if os.path.exists(csv_file_path):
                df = pd.read_csv(csv_file_path)

                # Loading JSON file for column names mappings
                config_json_file_path = Path(os.path.join(cwd, "config.json"))
                with open(config_json_file_path) as f:
                    data = json.load(f)
                    mappings = data[customer_name]
                
                del_rows = []
                
                # Renaming columns with concertiv id's
                headers = []
                for k, v in mappings.items():
                    headers.append(v)
                df.columns = headers
                
                df_headers = list(df.columns.values)
                for i in df_headers:
                    if i == '':
                        df.drop(['{0}'.format(i)], axis=1)
                
                df.drop(df[(df["Carrier Code"] == "2V") | (df["Carrier Code"] == "9F")].index, inplace=True)
                df.drop(df[(df["Origin Airport Code"] == "XXX") | (df["Origin Airport Code"] == "YYY") | (df["Origin Airport Code"] == "ZZZ")].index, inplace =True)
                
                # Get data from database tables
                prefered_qs = Preference.objects.filter(customer_name = customer_name).values_list('prefered_airline')
                prefered_airline_data = list(prefered_qs.values())
                
                airport_qs = Airport.objects.all()
                airport_data = list(airport_qs.values())

                airline_qs = Airline.objects.all()
                airline_data = list(airline_qs.values())

                alliance_qs = Alliance.objects.all()
                alliance_data = list(alliance_qs.values())

                # Converting airport and carrier codes in dataframe to list
                airport_ori_code = df["Origin Airport Code"].tolist()
                airport_dest_code = df["Destination Airport Code"].tolist()
                carrier_code = df["Carrier Code"].tolist()
                # Setting rows display
                pd.set_option('display.max_rows', 1500)

                # Forming dataframe for final data
                df['Departure Date'] = pd.to_datetime(df['Departure Date'], dayfirst=True)
                df.insert(0, "Travel Date Quarter", 'Q' + df['Departure Date'].dt.quarter.astype(str) + " " + df['Departure Date'].dt.year.astype(str), True)
                df.insert(1, "Travel Date Half Year", 'H' + df['Departure Date'].dt.month.gt(6).add(1).astype(str) + " " + df['Departure Date'].dt.year.astype(str), True)
                df.insert(2, "Receive Quarter", quarter + " " + year, True)
                df.insert(3, "Receive Half Year", self.half_year(quarter) + " " + year, True)
                df.insert(4, "PoS", country, True)
                df.insert(5, "Client", customer_name, True)
                df.insert(6, "Agency", travel_agency, True)
                df.insert(7, "Country", country, True)
                df["Carrier Name"] = [i["carrier_name"] for i in airline_data for cc in carrier_code for k, v in i.items() if cc == v]
                df["Origin City"] = [i["airport_city"] for oc in airport_ori_code for i in airport_data for k, v in i.items() if oc == v]
                df["Origin Country"] = ""
                df["Destination City"] = [i["airport_city"] for dc in airport_dest_code for i in airport_data for k, v in i.items() if dc == v]
                df["Destination Country"] = ""
                df["International vs. Domestic"] = ""
                df["Refund"] = ""
                df["Exchange"] = ""
                df["Refund / Exchange"] = ""
                df["CTV_Booking Class Code"] = df["Class of Service Code"]
                df["CTV_Origin_Airport_Id"] = [i["airport_id"] for oc in airport_ori_code for i in airport_data for k, v in i.items() if oc == v]
                df["CTV_Destination_Airport_Id"] = [i["airport_id"] for dc in airport_dest_code for i in airport_data for k, v in i.items() if dc == v]
                df["CTV_Reference"] = df["Origin Airport Code"] + "-" + df["Destination Airport Code"] + "-" + df["Class of Service Code"]
                df["CTV_Fare"] = df["Class of Service"]
                df["CTV_Carrier_Id"] = [i["carrier_id"] for cc in carrier_code for i in airline_data for k, v in i.items() if cc == v]
                df["CTV_Alliance_ID"] = [i["carrier_alliance_code_id"] for cc in carrier_code for i in airline_data for k, v in i.items() if cc == v]
                alliance_data_list = df["CTV_Alliance_ID"].tolist()
                df["Errors"] = ""
                df["Savings Alliance Classification"] = [i["alliance_name"] for adl in alliance_data_list for i in alliance_data for k, v in i.items() if adl == v]

                # Determine savings classifier based on departure data for Prism airlines
                savings_alliance_classifier = df["Savings Alliance Classification"].tolist()
                jet_departure_date_df = df.loc[df["Savings Alliance Classification"] == "JetBlue", "Departure Date"]
                jet_departure_date_df = jet_departure_date_df.astype(str)
                jet_departure_date = jet_departure_date_df.tolist()
                jet_booking_class_code_df = df.loc[df["Savings Alliance Classification"] == "JetBlue", "CTV_Booking Class Code"]
                jet_booking_class_code_df = jet_booking_class_code_df.astype(str)
                jet_booking_class_code = jet_booking_class_code_df.tolist()
                emi_references_df = df.loc[df["Savings Alliance Classification"] == "Emirates", "CTV_Reference"]
                emi_references_df = emi_references_df.astype(str)
                emi_references = emi_references_df.tolist()
                tur_references_df = df.loc[df["Savings Alliance Classification"] == "Turkish", "CTV_Reference"]
                tur_references_df = tur_references_df.astype(str)
                tur_references = tur_references_df.tolist()
                qan_references_df = df.loc[df["Savings Alliance Classification"] == "Qantas", "CTV_Reference"]
                qan_references_df = qan_references_df.astype(str)
                qan_references = qan_references_df.tolist()
                sin_references_df = df.loc[df["Savings Alliance Classification"] == "Singapore", "CTV_Reference"]
                sin_references_df = sin_references_df.astype(str)
                sin_references = sin_references_df.tolist()

                jet_ctv_references, emi_ctv_references, tur_ctv_references, qan_ctv_references, sin_ctv_references, jet_indexes, emi_indexes, tur_indexes, qan_indexes, sin_indexes = self.savings_classifier(savings_alliance_classifier, jet_departure_date, jet_booking_class_code, emi_references, tur_references, qan_references, sin_references)
                jet_tour_code, jet_ticket_designator, emi_tour_code, emi_ticket_designator, tur_tour_code, tur_ticket_designator, qan_tour_code, sin_tour_code, sin_ticket_designator = self.tour_code_and_ticket_designator()
                df["Departure Date"] = pd.to_datetime(df["Departure Date"]).dt.date

                contract_classifier, savings_tour_code, savings_ticket_designator, discount = [], [], [], []
                [contract_classifier.append("Not Preferred Airlines") for i in range(len(savings_alliance_classifier))]
                for i in savings_alliance_classifier:
                    if i == "JetBlue":
                        for j in range(len(jet_indexes)):
                            contract_classifier[jet_indexes[j]] = jet_ctv_references[j]
                    elif i == "Emirates":
                        for e in range(len(emi_indexes)):
                            contract_classifier[emi_indexes[e]] = emi_ctv_references[e]
                    elif i == "Turkish":
                        for t in range(len(tur_indexes)):
                            contract_classifier[tur_indexes[t]] = tur_ctv_references[t]
                    elif i == "Qantas":
                        for q in range(len(qan_indexes)):
                            contract_classifier[qan_indexes[q]] = qan_ctv_references[q]
                    elif i == "Singapore":
                        for s in range(len(sin_indexes)):
                            contract_classifier[sin_indexes[s]] = sin_ctv_references[s]
                
                df["Savings Contract Classifier"] = [j for j in contract_classifier]

                # Validating tour code and ticket designator
                for i in range(len(savings_alliance_classifier)):
                    savings_tour_code.append("Not Preferred Airlines")
                    savings_ticket_designator.append("Not Preferred Airlines")

                tour_code = df["Tour Code"].tolist()
                ticket_designator = df["Ticket Designator"].tolist()
                df["Tour Code"] = df["Tour Code"].astype(str)
                df["Ticket Designator"] = df["Ticket Designator"].astype(str)
                default_discount = 0.00
                [discount.append(default_discount) for i in range(len(savings_alliance_classifier))]

                # Checking tour code and ticket designator for Non Prism Flights
                for i in savings_alliance_classifier:
                    if i == "JetBlue":
                        discount, savings_tour_code, savings_ticket_designator = self.check_tour_code_and_ticket_designator(df, discount, savings_tour_code, savings_ticket_designator, customer_name, quarter, year, jet_indexes, jet_tour_code, jet_ticket_designator)
                    elif i == "Emirates":
                        discount, savings_tour_code, savings_ticket_designator = self.check_tour_code_and_ticket_designator(df, discount, savings_tour_code, savings_ticket_designator, customer_name, quarter, year, emi_indexes, emi_tour_code, emi_ticket_designator)
                    elif i == "Turkish":
                        discount, savings_tour_code, savings_ticket_designator = self.check_tour_code_and_ticket_designator(df, discount, savings_tour_code, savings_ticket_designator, customer_name, quarter, year, tur_indexes, tur_tour_code, tur_ticket_designator)
                    elif i == "Qantas":
                        discount, savings_tour_code, savings_ticket_designator = self.check_tour_code_and_ticket_designator(df, discount, savings_tour_code, savings_ticket_designator, customer_name, quarter, year, qan_indexes, qan_tour_code, "nan")
                    elif i == "Singapore":
                        discount, savings_tour_code, savings_ticket_designator = self.check_tour_code_and_ticket_designator(df, discount, savings_tour_code, savings_ticket_designator, customer_name, quarter, year, sin_indexes, sin_tour_code, sin_ticket_designator)

                df["Tour Code"] = [tc for tc in tour_code]
                df["Ticket Designator"] = [td for td in ticket_designator]
                df["Contract Classifier Tour Code"] = [tc for tc in savings_tour_code]
                df["Contract Classifier Ticket Designator"] = [td for td in savings_ticket_designator]
                discount_if_applied = []
                classifier_tour_code = df["Contract Classifier Tour Code"].tolist()
                classifier_ticket_designator = df["Contract Classifier Ticket Designator"].tolist()
                [discount_if_applied.append("Y") if ctc == "Available, Matched" or ctd == "Available, Matched" else discount_if_applied.append("N") for ctc, ctd in zip(classifier_tour_code, classifier_ticket_designator)]
                df["If Discount Applied"] = [da for da in discount_if_applied]
                df["Discount"] = [d for d in discount]
                pre_dis, pre, sav = [], [], []
                fare = df["Fare"].tolist()
                discount = df["Discount"].tolist()
                pre_dis, pre, sav, reference_code_missing, non_prism = [], [], [], [], []
                [reference_code_missing.append("Y") if d == 99999.9 else reference_code_missing.append("N") for d in discount]
                df["If Reference Missing"] = [ref for ref in reference_code_missing]
                [pre.append(1 - d) for d in discount]
                [pre_dis.append(f / d) for f, d in zip(fare, pre)]
                df["Pre-Discount Cost"] = [pr for pr in pre_dis]
                df["Pre-Discount Cost"] = df["Pre-Discount Cost"].round(2)
                pre_disc_cost = df["Pre-Discount Cost"].tolist()
                [sav.append(pre - f) for f, pre in zip(fare, pre_disc_cost)]
                df["Savings"] = [s for s in sav]
                df["Savings"] = df["Savings"].round(2)
                data = self.config_path()
                for ali in range(len(savings_alliance_classifier)):
                    non_prism.append("Y")
                    if savings_alliance_classifier[ali] in data["group_deals"]:
                        non_prism[ali] = "N"
                df["Non-Prism Preferred"] = [np for np in non_prism]

                # Rearranging the columns
                headers = ["Travel Date Quarter", "Travel Date Half Year", "Receive Quarter", "Receive Half Year", "PoS", "Client", "Agency", 
                        "Country", "Traveller Name", "Booked Date / Invoice Date", "Departure Date",
                        "Carrier Code", "Carrier Name", "Class of Service Code", "Class of Service", "Fare Basis Code",
                        "Origin Airport Code", "Origin City", "Origin Country", "Destination Airport Code", "Destination City",
                        "Destination Country", "Itinerary / Routing", "Tour Code", "Ticket Designator", "Point of Sale", "Fare", "Tax", "Refund",
                        "Exchange", "Refund / Exchange", "Booking Source", "Leg Counter", "Miles / Mileage",
                        "International vs. Domestic", "PNR Locator", "CTV_Booking Class Code", "CTV_Origin_Airport_Id", "CTV_Destination_Airport_Id",
                        "CTV_Reference", "CTV_Fare", "CTV_Carrier_Id", "CTV_Alliance_ID", "Errors", "Savings Alliance Classification",
                        "Savings Contract Classifier", "Discount", "Pre-Discount Cost", "Savings", "Non-Prism Preferred",
                        "Contract Classifier Tour Code", "Contract Classifier Ticket Designator", "If Discount Applied", "If Reference Missing"]

                df = df.reindex(columns=headers)

                # Reading Prism flights data
                n = 4
                prism_airlines_discount_list, vol_list, net_list, sav_list, total_list = [], [], [], [], []
                total_prism_pre_discount, total_prism_actual_spend, total_prism_savings, total_prism_vol, total_prism_net = 0.0, 0.0, 0.0, 0.0, 0.0
                total_list.append("Total")
                prism_airlines = ["American / Oneworld", "Delta / SkyTeam", "United / Star Alliance"]
                quarter_year = quarter + " " + year
                win_etl_file_path = self.base_path()
                new_file_path = Path(os.path.join(win_etl_file_path, customer_name, "3. Performance Reports", year, quarter, "Raw TMC Data-Dev"))
                prism_file_name = "Air PRISM & Other.xlsx"
                csv_prism_file_name = "Air PRISM & Other.csv"
                file_path = Path(os.path.join(new_file_path, prism_file_name))
                csv_file_path = Path(os.path.join(new_file_path, csv_prism_file_name))
                prism_airlines_discount = self.prism_flights_info(file_path, csv_file_path, quarter_year, prism_airlines)
                prism_airlines_discount_list = [prism_airlines_discount[i * n:(i + 1) * n] for i in range((len(prism_airlines_discount) + n - 1) // n)]
                for p in range(len(prism_airlines)):
                    x = df.index[df["Savings Alliance Classification"] == prism_airlines[p]].tolist()
                    vol = len(x) / len(df.index)
                    vol = vol * 100
                    total_prism_vol = total_prism_vol + vol
                    p_vol = "{:,.2f}".format(vol) + "%"
                    vol_list.append(p_vol)
                    prism_sum_pre_discount = float(prism_airlines_discount_list[p][1])
                    total_prism_pre_discount = total_prism_pre_discount + prism_sum_pre_discount
                    prism_sum_actual_spend = float(prism_airlines_discount_list[p][2])
                    total_prism_actual_spend = total_prism_actual_spend + prism_sum_actual_spend
                    prism_sum_savings = float(prism_airlines_discount_list[p][3])
                    total_prism_savings = total_prism_savings + prism_sum_savings
                    net = (prism_sum_actual_spend / prism_sum_pre_discount) * 100
                    total_prism_net = total_prism_net + net
                    prism_airlines_discount_list[p][1] = "$" + "{:,.2f}".format(prism_airlines_discount_list[p][1])
                    prism_airlines_discount_list[p][2] = "$" + "{:,.2f}".format(prism_airlines_discount_list[p][2])
                    prism_airlines_discount_list[p][3] = "$" + "{:,.2f}".format(prism_airlines_discount_list[p][3])
                    p_net = "{:,.2f}".format(net) + "%"
                    net_list.append(p_net)
                    sav_list.append(prism_airlines_discount_list[p][3])
                for pa, i, j, k in zip(prism_airlines_discount_list, vol_list, net_list, sav_list):
                    pa.insert(3, i)
                    pa.insert(5, j)
                    pa.insert(6, k)

                # Final report after CPR process
                jet_blue_list, emi_list, tur_list, qan_list, sin_list, non_prism_list = [], [], [], [], [], []
                for i in prefered_airline_data:
                    for k, v in i.items():
                        if v == "JetBlue":
                            sum_jet_pre_dis_cost = df.loc[df["Savings Alliance Classification"] == "JetBlue", "Pre-Discount Cost"].sum()
                            sum_jet_fare = df.loc[df["Savings Alliance Classification"] == "JetBlue", "Fare"].sum()
                            sum_jet_savings = df.loc[df["Savings Alliance Classification"] == "JetBlue", "Savings"].sum()
                            jet_blue_list.append("JetBlue")
                            jet_blue_list, total_non_prism_pre_discount, total_non_prism_actual_spend, total_non_prism_vol, total_non_prism_savings, total_non_prism_net, total_non_prism_final_savings = self.calculate_total(df, jet_blue_list, jet_indexes, sum_jet_pre_dis_cost, sum_jet_fare, sum_jet_savings, total_prism_pre_discount, total_prism_actual_spend, total_prism_vol, total_prism_savings, total_prism_net)
                            non_prism_list.append(jet_blue_list)
                        elif v == "Emirates":
                            sum_emi_pre_dis_cost = df.loc[df["Savings Alliance Classification"] == "Emirates", "Pre-Discount Cost"].sum()
                            sum_emi_fare = df.loc[df["Savings Alliance Classification"] == "Emirates", "Fare"].sum()
                            sum_emi_savings = df.loc[df["Savings Alliance Classification"] == "Emirates", "Savings"].sum()
                            emi_list.append("Emirates")
                            emi_list, total_non_prism_pre_discount, total_non_prism_actual_spend, total_non_prism_vol, total_non_prism_savings, total_non_prism_net, total_non_prism_final_savings = self.calculate_total(df, emi_list, emi_indexes, sum_emi_pre_dis_cost, sum_emi_fare, sum_emi_savings, total_prism_pre_discount, total_prism_actual_spend, total_prism_vol, total_prism_savings, total_prism_net)
                            non_prism_list.append(emi_list)
                        elif v == "Turkish":
                            sum_tur_pre_dis_cost = df.loc[df["Savings Alliance Classification"] == "Turkish", "Pre-Discount Cost"].sum()
                            sum_tur_fare = df.loc[df["Savings Alliance Classification"] == "Turkish", "Fare"].sum()
                            sum_tur_savings = df.loc[df["Savings Alliance Classification"] == "Turkish", "Savings"].sum()
                            tur_list.append("Turkish")
                            tur_list, total_non_prism_pre_discount, total_non_prism_actual_spend, total_non_prism_vol, total_non_prism_savings, total_non_prism_net, total_non_prism_final_savings = self.calculate_total(df, tur_list, tur_indexes, sum_tur_pre_dis_cost, sum_tur_fare, sum_tur_savings, total_prism_pre_discount, total_prism_actual_spend, total_prism_vol, total_prism_savings, total_prism_net)
                            non_prism_list.append(tur_list)
                        elif v == "Qantas":
                            sum_qan_pre_dis_cost = df.loc[df["Savings Alliance Classification"] == "Qantas", "Pre-Discount Cost"].sum()
                            sum_qan_fare = df.loc[df["Savings Alliance Classification"] == "Qantas", "Fare"].sum()
                            sum_qan_savings = df.loc[df["Savings Alliance Classification"] == "Qantas", "Savings"].sum()
                            qan_list.append("Qantas")
                            qan_list, total_non_prism_pre_discount, total_non_prism_actual_spend, total_non_prism_vol, total_non_prism_savings, total_non_prism_net, total_non_prism_final_savings = self.calculate_total(df, qan_list, qan_indexes, sum_qan_pre_dis_cost, sum_qan_fare, sum_qan_savings, total_prism_pre_discount, total_prism_actual_spend, total_prism_vol, total_prism_savings, total_prism_net)
                            non_prism_list.append(qan_list)
                        elif v == "Singapore":
                            sum_sin_pre_dis_cost = df.loc[df["Savings Alliance Classification"] == "Singapore", "Pre-Discount Cost"].sum()
                            sum_sin_fare = df.loc[df["Savings Alliance Classification"] == "Singapore", "Fare"].sum()
                            sum_sin_savings = df.loc[df["Savings Alliance Classification"] == "Singapore", "Savings"].sum()
                            sin_list.append("Singapore")
                            sin_list, total_non_prism_pre_discount, total_non_prism_actual_spend, total_non_prism_vol, total_non_prism_savings, total_non_prism_net, total_non_prism_final_savings = self.calculate_total(df, sin_list, sin_indexes, sum_sin_pre_dis_cost, sum_sin_fare, sum_sin_savings, total_prism_pre_discount, total_prism_actual_spend, total_prism_vol, total_prism_savings, total_prism_net)
                            non_prism_list.append(sin_list)
                        
                
                # Values to populate on graphs
                final_pre_discount = total_non_prism_pre_discount + total_prism_pre_discount
                request.session['final_pre_discount'] = final_pre_discount
                final_savings = total_non_prism_savings + total_prism_savings
                request.session['final_savings'] = final_savings
                actual_spend = total_non_prism_actual_spend + total_prism_actual_spend
                request.session['actual_spend'] = actual_spend
                
                total_non_prism_pre_discount = "$" + "{:,.2f}".format(total_non_prism_pre_discount)
                total_list.append(total_non_prism_pre_discount)
                total_non_prism_actual_spend = "$" + "{:,.2f}".format(total_non_prism_actual_spend)
                total_list.append(total_non_prism_actual_spend)
                total_non_prism_vol = "{:,.2f}".format(total_non_prism_vol) + "%"
                total_list.append(total_non_prism_vol)
                total_non_prism_savings = "$" + "{:,.2f}".format(total_non_prism_savings)
                total_list.append(total_non_prism_savings)
                total_non_prism_net = "{:,.2f}".format(total_non_prism_net) + "%"
                total_list.append(total_non_prism_net)
                total_non_prism_final_savings = "$" + "{:,.2f}".format(total_non_prism_final_savings)
                total_list.append(total_non_prism_final_savings)
                
                table = {"non_prism_list": non_prism_list, "prism_list": prism_airlines_discount_list, "total_list": total_list}

                # Writing new column names into separate .xlsx file
                win_etl_file_path = self.base_path()
                new_file_path = Path(os.path.join(win_etl_file_path, customer_name, "3. Performance Reports", year, quarter, "Raw TMC Data-Dev"))
                new_file_name = customer_name + "_Air_" + quarter + year + "_"+ country +"_FinalData" + ".xlsx"
                file_name = Path(os.path.join(new_file_path, new_file_name))
                df.to_excel(file_name, encoding='utf8', index=False)
                
                os.chdir(cwd)
                context = {'table': table, 'customer_name': customer_name, 'quarter': quarter, 'year': year}
                return render(request, self.template_name, context=context)
        except FileNotFoundError:
            message = ("Unable to find CSV file in specified directory: %s" % csv_file_path)
            context = {'message': message}
            return render(request, self.error_url, context)
        finally:
                # Deleting previous version of CSV - raw9* data file
                os.chdir(new_file_path)
                pre_csv_file = customer_name + "_Air_" + quarter + year + "_" + country + ".csv"
                if os.path.exists(pre_csv_file):
                    os.remove(pre_csv_file)

                # Deleting previous version of CSV - group mappings airline discounts file
                csv_file_path = Path(os.path.join(new_file_path, "Group Airline Discounts Mapping.csv"))
                if os.path.exists(csv_file_path):
                    os.remove(csv_file_path)

                # Deleting CSV file - Air Prism & Other files
                # air_prism_file = Path(os.path.join(new_file_path, "Air PRISM & Other.csv"))
                # if os.path.exists(air_prism_file):
                #     os.remove(air_prism_file)          
            
    
class GraphsView(TemplateView):
    cwd = os.getcwd()
    os.chdir(cwd)
    template_name = 'air/get_graphs.html'
    
    def post(self, request):
        customer_name = request.session.get("customer_name")
        quarter = request.session.get("quarter")
        year = request.session.get("year")
        final_pre_discount = request.session['final_pre_discount']
        final_savings = request.session['final_savings']
        actual_spend = request.session['actual_spend']
        data = {"prediscount": final_pre_discount, "savings": final_savings, "spend": actual_spend}
        context={'graph':data, 'customer_name': customer_name, 'quarter': quarter, 'year': year}
        return render(request, self.template_name, context)
