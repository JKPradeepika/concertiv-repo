from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from .forms import *
from .models import *

from pathlib import Path, PureWindowsPath
import os
import json
import pandas as pd

# Create your views here.
class BasicView(View):
    # Function to return config file path
    def config_path(self):
        cwd = os.getcwd()
        config_json_file_path = Path(os.path.join(cwd,"static", "json", "config.json"))
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
    def savings_classifier(self, classifier_names, jet_departure_date, jet_booking_class_code, emi_references, tur_references, qan_references, sin_departure_date):
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
            [jet_ctv_references.append(''.join("Pre May 2019"+"-"+bc)) if jet_departure_date[jd] <= dd else jet_ctv_references.append(''.join("Post May 2019"+"-"+bc)) for bc in jet_booking_class_code[jd]]
        [emi_ctv_references.append(e) for e in emi_references]
        [tur_ctv_references.append(t) for t in tur_references]
        [qan_ctv_references.append(q) for q in qan_references]
        dd1 = data["sin_departure_date"]
        [sin_ctv_references.append(''.join("Pre July 2019")) if sin_departure_date[sd] <= dd1 else sin_ctv_references.append(''.join("Post July 2019")) for sd in range(len(sin_departure_date))]
        return jet_ctv_references, emi_ctv_references, tur_ctv_references, qan_ctv_references, sin_ctv_references, jet_indexes, emi_indexes, tur_indexes, qan_indexes, sin_indexes 

    # Function to return tour code and ticket designator for all Prism airlines based on savings contract classifier
    def tour_code_and_ticket_designator(self):
        data = self.config_path()
        tour_code_and_ticket_designator = data["tour_code_and_ticket_designator"]
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
        return path
    
    # Function to assign discount based on reference_list
    def assign_discount(self, discount, discount_reference_list, indices_list, reference_list, contract_list, sin_references, sin_ctv_references, df):
        loc_list = []
        if (len(sin_references) > 0) and (discount_reference_list == sin_ctv_references):
            for i,j in zip(discount_reference_list, sin_references):
                if i in contract_list and j in reference_list:
                    index = int(df[(df["Reference"]==j) & (df["Contract"] == i)].index[0])
                    loc = df.at[index, "Discount"]
                    loc_list.append(loc)
                else:
                    loc_list.append("Reference is missing")
            p = dict(zip(indices_list, loc_list))
            m = list(p.values())
            j = list(p.keys())
            for i in range(len(discount)):
                for k in range(len(j)):
                    if i == j[k]:
                        discount[i] = m[k]
        else:
            for tk in discount_reference_list:
                if tk in reference_list:
                    index = int(df[df["Reference"]==tk].index[0])
                    loc = df.at[index, "Discount"]
                    loc_list.append(loc)
                else:
                    loc_list.append("Reference is missing")
            p = dict(zip(indices_list, loc_list))
            m = list(p.values())
            j = list(p.keys())
            for i in range(len(discount)):
                for k in range(len(j)):
                    if i == j[k]:
                        discount[i] = m[k] 
        return discount

    # Function to find discount based on reference for each savings classifier
    def find_discount_on_tour_code_and_ticket_designator(self, data_frame, discount, discount_reference_list, indices_list, customer_name, quarter, year, alliance_savings_classifier):
        sin_references_df = data_frame.loc[data_frame["Savings Alliance Classification"] == "Singapore", "CTV_Reference"]
        sin_references_df = sin_references_df.astype(str)
        sin_references = sin_references_df.tolist()
        sin_ctv_references = data_frame.loc[data_frame["Savings Alliance Classification"] == "Singapore", "Savings Contract Classifier"]
        sin_ctv_references = sin_ctv_references.astype(str)
        sin_ctv_references = sin_ctv_references.tolist()
        path = self.read_group_mappings(customer_name, quarter, year)
        full_file_path = Path(os.path.join(path, "Group Airline Discounts Mapping.xlsx"))
        csv_file_path = Path(os.path.join(path, "Group Airline Discounts Mapping.csv"))
        xl = pd.ExcelFile(full_file_path)
        df = pd.read_excel(xl, sheet_name=None)
        df = pd.concat(df, ignore_index=True)
        df.to_csv(csv_file_path, encoding='utf8', index=False)
        df = pd.read_csv(csv_file_path)
        reference_list = df["Reference"].tolist()
        contract_list = df["Contract"].tolist()
        discount = self.assign_discount(discount, discount_reference_list, indices_list, reference_list, contract_list, sin_references, sin_ctv_references, df)
        return discount  

    # Function to check whether the tour code and ticket designator are available or not to determine discount
    def check_tour_code_and_ticket_designator(self, df, discount, savings_tour_code, savings_ticket_designator, customer_name, quarter, year, index_list, tour_code, ticket_designator):
        alliance_savings_classifier = df["Savings Alliance Classification"].tolist()
        discount_contract_classifier = df["Savings Contract Classifier"].tolist()
        discount_reference_list, indices_list = [], []
        for i in range(len(index_list)):
            if df["Tour Code"].iloc[index_list[i]] == "nan" and df["Ticket Designator"].iloc[index_list[i]] == ticket_designator:
                discount_reference_list.append(discount_contract_classifier[index_list[i]])
                indices_list.append(index_list[i])
                savings_tour_code[index_list[i]] = "Not Available, Not Matched"
                savings_ticket_designator[index_list[i]] = "Available, Matched"
                self.find_discount_on_tour_code_and_ticket_designator(df, discount, discount_reference_list, indices_list, customer_name, quarter, year, alliance_savings_classifier)
            
            elif df["Tour Code"].iloc[index_list[i]] == tour_code and df["Ticket Designator"].iloc[index_list[i]] == "nan":
                discount_reference_list.append(discount_contract_classifier[index_list[i]])
                indices_list.append(index_list[i])
                savings_tour_code[index_list[i]] = "Available, Matched"
                savings_ticket_designator[index_list[i]] = "Not Available, Not Matched"
                self.find_discount_on_tour_code_and_ticket_designator(df, discount, discount_reference_list, indices_list, customer_name, quarter, year, alliance_savings_classifier)
                
            elif df["Tour Code"].iloc[index_list[i]] == tour_code and df["Ticket Designator"].iloc[index_list[i]] != "nan":
                discount_reference_list.append(discount_contract_classifier[index_list[i]])
                indices_list.append(index_list[i])
                savings_tour_code[index_list[i]] = "Available, Matched"
                if df["Ticket Designator"].iloc[index_list[i]] != ticket_designator:
                    savings_ticket_designator[index_list[i]] = "Available, Not Matched - " + df["Ticket Designator"].iloc[index_list[i]]
                else:
                    savings_ticket_designator[index_list[i]] = "Available, Matched"
                self.find_discount_on_tour_code_and_ticket_designator(df, discount, discount_reference_list, indices_list, customer_name, quarter, year, alliance_savings_classifier)
            
            elif df["Tour Code"].iloc[index_list[i]] != "nan" and df["Ticket Designator"].iloc[index_list[i]] == ticket_designator:
                discount_reference_list.append(discount_contract_classifier[index_list[i]])
                indices_list.append(index_list[i])
                if df["Tour Code"].iloc[index_list[i]] != tour_code:
                    savings_tour_code[index_list[i]] = "Available, Not Matched - " + df["Tour Code"].iloc[index_list[i]]
                else:
                    savings_tour_code[index_list[i]] = "Available, Matched"
                savings_ticket_designator[index_list[i]] = "Available, Matched"
                self.find_discount_on_tour_code_and_ticket_designator(df, discount, discount_reference_list, indices_list, customer_name, quarter, year, alliance_savings_classifier)
            
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

class HomeView(TemplateView):
    template_name = 'home.html'

class RawDataView(BasicView):
    template_name = 'air/raw_data.html'
    form_class = RawdataForm
    success_url = 'air/get_raw_data.html'

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
                elif file_name.startswith(customer_name) and file_name.__contains__("Air")and file_name.__contains__(quarter) and file_name.__contains__(year) and file_name.__contains__(country) and file_name.__contains__(".xlsx"):                 
                    file_path = os.path.join(path, file_name)
                    csv_file = customer_name + "_Air_" + quarter + year + ".csv"
                    csv_file_path = os.path.join(path, csv_file)
                    request.session['csv_file_path'] = csv_file_path
            if os.path.exists(file_path):       
                message = "Found the file. Click below to process the file"
                xl = pd.ExcelFile(file_path)
                for sheet in xl.sheet_names:
                    df = pd.read_excel(xl, sheet_name=sheet)
                    df.to_csv(csv_file_path, encoding='utf8', index=False)
            else:
                message = "File not found. Please check the path and Try again."
            context = {'form': form,'file_path': file_path, 'message': message, }
            return render(request, self.success_url, context)
        else:
            form = self.form_class(request.POST)
        return render(request, self.template_name, {'form': form})


class ProcessDataView(BasicView):
    template_name = 'air/process_data.html'


    def post(self, request, *args, **kwargs):
        cwd = os.getcwd()
        csv_file_path = request.session['csv_file_path']
        customer_name = request.session['customer_name']
        year = request.session['year']
        quarter = request.session['quarter']
        travel_agency = request.session['travel_agency']
        country = request.session['country']

        # Reading CSV file
        df = pd.read_csv(csv_file_path)

        # Loading JSON file for column names mappings
        config_json_file_path = Path(os.path.join(cwd,"static", "json", "config.json"))
        with open(config_json_file_path) as f:
            data = json.load(f)
            mappings = data[customer_name]
        
        del_col_names, del_rows = [], []
        # Renaming columns with concertiv id's
        df.rename(columns=mappings, inplace=True)

        # Dropping unnecessary columns
        col_name = df.columns.values.tolist()
        del_col_names = [i for i in col_name if i[0].islower()]
        df.drop(columns=del_col_names, inplace=True, axis=1)

        # Dropping unnecessary rows
        non_airport_codes = ["RTE-2V", "NYP-2V", "PHL-2V", "SEAAV", "BBY-2V", "PVD-2V", "HUD-2V", "WAS-2V", "XXX"]
        for i in non_airport_codes:
            if df["Origin Airport Code"].str.contains(i).any():
                del_rows = (df[df["Origin Airport Code"].str.contains(i)].index.values)
                df.drop(del_rows, inplace=True, axis=0)
        
        # Get data from database tables
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
        df.insert(1, "Travel Date Half Year", 'H' + df['Departure Date'].dt.month.gt(6).add(1).astype(str) + " "+df['Departure Date'].dt.year.astype(str), True)
        df.insert(2, "Receive Quarter", quarter + " " + year, True)
        df.insert(3, "Receive Half Year", self.half_year(quarter) + " " + year, True)
        df.insert(4, "PoS", country, True)
        df.insert(5, "Client", customer_name, True)
        df.insert(6, "Agency", travel_agency, True)
        df.insert(7, "Country", df["Point of Sale"], True)

        df["Carrier Name"] = [v for cc in carrier_code for i in airline_data for k, v in i.items() if cc == v]
        df["Origin City"] = [v for oc in airport_ori_code for i in airport_data for k, v in i.items() if oc == v]
        df["Origin Country"] = ""
        df["Destination City"] = [v for dc in airport_dest_code for i in airport_data for k, v in i.items() if dc == v]
        df["Destination Country"] = ""
        df["International vs. Domestic"] = ""
        df["Refund"] = ""
        df["Exchange"] = ""
        df["Refund / Exchange"] = ""
        df["CTV_Booking Class Code"] = df["Class of Service Code"]
        booking_class_code = df["CTV_Booking Class Code"].tolist()
        df["CTV_Origin_Airport_Id"] = [v for oc in airport_ori_code for i in airport_data for k, v in i.items() if oc == v]
        df["CTV_Destination_Airport_Id"] = [v for dc in airport_dest_code for i in airport_data for k, v in i.items() if dc == v]
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
        sin_departure_date_df = df.loc[df["Savings Alliance Classification"] == "Singapore", "Departure Date"]
        sin_departure_date_df = sin_departure_date_df.astype(str)
        sin_departure_date = sin_departure_date_df.tolist()
        sin_references_df = df.loc[df["Savings Alliance Classification"] == "Singapore", "CTV_Reference"]
        sin_references_df = sin_references_df.astype(str)
        sin_references = sin_references_df.tolist()
        jet_ctv_references, emi_ctv_references, tur_ctv_references, qan_ctv_references, sin_ctv_references, jet_indexes, emi_indexes, tur_indexes, qan_indexes, sin_indexes = self.savings_classifier(savings_alliance_classifier, jet_departure_date, jet_booking_class_code, emi_references, tur_references, qan_references, sin_departure_date)
        jet_tour_code, jet_ticket_designator, emi_tour_code, emi_ticket_designator, tur_tour_code, tur_ticket_designator, qan_tour_code, sin_tour_code, sin_ticket_designator = self.tour_code_and_ticket_designator()
        df["Departure Date"] = pd.to_datetime(df["Departure Date"]).dt.date
        
        contract_classifier, savings_tour_code, savings_ticket_designator, discount = [], [], [], []
        [contract_classifier.append("Not Preferred Airlines") for i in range(len(savings_alliance_classifier))]
        for i in range(len(savings_alliance_classifier)):
            if savings_alliance_classifier[i] == "JetBlue":
                for j in range(len(jet_indexes)):
                    contract_classifier[jet_indexes[j]] = jet_ctv_references[j]
            elif savings_alliance_classifier[i] == "Emirates":
                for e in range(len(emi_indexes)):
                    contract_classifier[emi_indexes[e]] = emi_ctv_references[e]
            elif savings_alliance_classifier[i] == "Turkish":
                for t in range(len(tur_indexes)):
                    contract_classifier[tur_indexes[t]] = tur_ctv_references[t]
            elif savings_alliance_classifier[i] == "Qantas":
                for q in range(len(qan_indexes)):
                    contract_classifier[qan_indexes[q]] = qan_ctv_references[q]
            elif savings_alliance_classifier[i] == "Singapore":
                for s in range(len(sin_indexes)):
                    contract_classifier[sin_indexes[s]] = sin_ctv_references[s]
        df["Savings Contract Classifier"] = [j for j in contract_classifier]
        
        # Validating tour code and ticket designator
        contract_discount_classifier = df["Savings Contract Classifier"].tolist()
        for i in range(len(savings_alliance_classifier)):
            savings_tour_code.append("Not Preferred Airlines")
            savings_ticket_designator.append("Not Preferred Airlines")
        
        
        tour_code = df["Tour Code"].tolist()
        ticket_designator = df["Ticket Designator"].tolist()
        df["Tour Code"] = df["Tour Code"].astype(str)
        df["Ticket Designator"] = df["Ticket Designator"].astype(str)
        default_discount = 0.00
        [discount.append(default_discount) for i in range(len(savings_alliance_classifier))]
        
        # discount, savings_tour_code, savings_ticket_designator = self.check_tour_code_and_ticket_designator(df, discount, savings_tour_code, savings_ticket_designator, customer_name, quarter, year, jet_indexes, jet_tour_code, jet_ticket_designator, emi_indexes, emi_tour_code, emi_ticket_designator)
        for i in range(len(savings_alliance_classifier)):
            if savings_alliance_classifier[i] == "JetBlue":
                discount, savings_tour_code, savings_ticket_designator = self.check_tour_code_and_ticket_designator(df, discount, savings_tour_code, savings_ticket_designator, customer_name, quarter, year, jet_indexes, jet_tour_code, jet_ticket_designator)
            elif savings_alliance_classifier[i] == "Emirates":
                discount, savings_tour_code, savings_ticket_designator = self.check_tour_code_and_ticket_designator(df, discount, savings_tour_code, savings_ticket_designator, customer_name, quarter, year, emi_indexes, emi_tour_code, emi_ticket_designator)
            elif savings_alliance_classifier[i] == "Turkish":
                discount, savings_tour_code, savings_ticket_designator = self.check_tour_code_and_ticket_designator(df, discount, savings_tour_code, savings_ticket_designator, customer_name, quarter, year, tur_indexes, tur_tour_code, tur_ticket_designator)
            elif savings_alliance_classifier[i] == "Qantas":
                discount, savings_tour_code, savings_ticket_designator = self.check_tour_code_and_ticket_designator(df, discount, savings_tour_code, savings_ticket_designator, customer_name, quarter, year, qan_indexes, qan_tour_code, "nan")
            elif savings_alliance_classifier[i] == "Singapore":
                discount, savings_tour_code, savings_ticket_designator = self.check_tour_code_and_ticket_designator(df, discount, savings_tour_code, savings_ticket_designator, customer_name, quarter, year, sin_indexes, sin_tour_code, sin_ticket_designator)
        
        df["Tour Code"] = [tc for tc in tour_code]
        df["Ticket Designator"] = [td for td in ticket_designator]
        df["Contract Classifier Tour Code"] = [tc for tc in savings_tour_code]
        df["Contract Classifier Ticket Designator"] = [td for td in savings_ticket_designator]
        discount_if_applied = []
        classifier_tour_code = df["Contract Classifier Tour Code"].tolist()
        classifier_ticket_designator = df["Contract Classifier Ticket Designator"].tolist()
        for ctc, ctd in zip(classifier_tour_code, classifier_ticket_designator):
            if ctc == "Available, Matched" or ctd == "Available, Matched":
                discount_if_applied.append("Y")
            else:
                discount_if_applied.append("N")
        df["If Discount Applied"] = [da for da in discount_if_applied]
        df["Discount"] = [d for d in discount]
        
        # Rearranging the columns
        headers = ["Travel Date Quarter", "Travel Date Half Year", "Receive Quarter", "Receive Half Year", "PoS", "Client",
                   "Agency", "Country", "Traveller Name", "Booked Date / Invoice Date", "Departure Date", "Carrier Code",
                   "Carrier Name", "Class of Service Code", "Class of Service", "Fare Basis Code", "Origin Airport Code",
                   "Origin City", "Origin Country", "Destination Airport Code", "Destination City", "Destination Country",
                   "Itinerary / Routing", "Tour Code", "Ticket Designator", "Point of Sale", "Fare", "Tax", "Refund", "Exchange",
                   "Refund / Exchange", "Booking Source", "Leg Counter", "Miles / Mileage", "International vs. Domestic",
                   "PNR Locator", "CTV_Booking Class Code", "CTV_Origin_Airport_Id", "CTV_Destination_Airport_Id", "CTV_Reference",
                   "CTV_Fare", "CTV_Carrier_Id", "CTV_Alliance_ID", "Errors", "Savings Alliance Classification", 
                   "Savings Contract Classifier", "Contract Classifier Tour Code", "Contract Classifier Ticket Designator", 
                   "If Discount Applied", "Discount"]
                #    ,
                #    , , "Pre-Discount Cost", "Savings", "Non-Prism Preferred"]
        
        df = df.reindex(columns=headers)

        # Writing new column names into separate .xlsx file
        win_etl_file_path = self.base_path()
        new_file_path = Path(os.path.join(win_etl_file_path, customer_name, "3. Performance Reports", year, quarter, "Raw TMC Data-Dev"))
        new_file_name = customer_name+"_Air_"+quarter+year+"_FinalData"+".xlsx"
        file_name = Path(os.path.join(new_file_path, new_file_name))
        df.to_excel(file_name, encoding='utf8', index=False)

        # Deleting previous version of CSV - raw data file
        os.chdir(new_file_path)
        pre_csv_file = customer_name+"_Air_"+quarter+year+".csv"
        if os.path.exists(pre_csv_file):
            os.remove(pre_csv_file)

        # Deleting previous version of CSV - group mappings airline discounts file
        csv_file_path = Path(os.path.join(new_file_path, "Group Airline Discounts Mapping.csv"))
        if os.path.exists(csv_file_path):
            os.remove(csv_file_path)
        
        return HttpResponse(alliance_data, content_type="application/json")

    
