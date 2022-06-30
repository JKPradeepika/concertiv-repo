import csv
import json
from operator import index
import os
from matplotlib.pyplot import prism
import pandas as pd
from . import forms
from django.shortcuts import render
from pathlib import Path, PureWindowsPath

# Wrtie all helper functions here

# To find username of the system administrator
def files_path():
    cwd = os.getcwd()
    config_json_file_path = Path(os.path.join(cwd,"static", "json", "config.json"))
    with open(config_json_file_path) as f:
        data = json.load(f)
    username = os.getlogin()
    user_path = Path(os.path.join("C:/Users", username))
    elt_file_path = data["win_etl_output_files_path"]
    win_etl_file_path = Path(os.path.join(user_path, elt_file_path))
    return win_etl_file_path

# Function which returns Year Half based on Quarter
def half_year(quarter):
    if quarter == "Q1" or quarter == "Q2":
        return "H1"
    else:
        return "H2"

# Function to read Group Mappings for Preferred Savings Classifiers
def read_group_mappings():
    username = os.getlogin()
    user_path = Path(os.path.join("C:/Users", username))
    group_deals_path = Path(os.path.join(user_path, "Dropbox (Concertiv)", "Ve Arc Sharing", "Group Airline Discount Mapping", "Group Airline Discounts"))
    path = PureWindowsPath(group_deals_path)
    full_file_path = Path(os.path.join(path, "Group Airline Discounts Mapping.xlsx"))
    csv_file_path = Path(os.path.join(path, "Group Airline Discounts Mapping.csv"))
    return full_file_path, csv_file_path


# Function to assign discount based on reference_list
def assign_discount(disc, discount_list, index_list,  reference_list, df):
    loc_list = []
    for tk in discount_list:
        if tk in reference_list:
            loc = df.loc[df["Reference"] == tk, "Discount"].iloc[0]
            loc_list.append(loc)
    p = dict(zip(index_list, loc_list))
    m = list(p.values())
    j = list(p.keys())
    for i in range(len(disc)):
        for k in range(len(j)):
            if i == j[k]:
                disc[i] = m[k] 
    return disc


# Function to get prism airlines information
def get_prism_airline_info(file_path, csv_file_path, quarter, prism_airlies):
    prism_disc_lst = []
    xl = pd.ExcelFile(file_path)
    for sheet in xl.sheet_names:
        if sheet == "Air - PRISM & Other":
            df = pd.read_excel(xl, sheet_name=sheet)
            df.to_csv(csv_file_path, encoding='utf8', index=False)
            df = pd.read_csv(csv_file_path)
            index_list = df.index[df["Quarter"] == quarter].tolist()
    for il, c in zip(index_list, prism_airlies):
        prism_disc_lst.append(c)
        pre_dis = df.iloc[il]["Pre-Discount"]
        pre_dis = pre_dis.round(2)
        pre_dis = pre_dis.astype("str")
        prism_disc_lst.append(pre_dis)
        act_spe = df.iloc[il]["Actual Spend"]
        act_spe = act_spe.round(2)
        act_spe = act_spe.astype(str)
        prism_disc_lst.append(act_spe)
        sav = df.iloc[il]["Savings"]
        sav = sav.round(2)
        sav = sav.astype(str)
        sav = "$" + sav
        prism_disc_lst.append(sav)
    return prism_disc_lst
       

# Function which whether it is Pre-May or Post-May for JetBlue
def savings_classifier(alliance_names, departure_date, booking_class_code, emi_reference_lst, tur_reference_lst, qan_reference_lst, sing_departure_date):
    jet_references, jet_indexes, emi_references, emi_indexes, tur_references, tur_indexes, qan_references, qan_indexes, sing_references, sing_indexes = [], [], [], [], [], [], [], [], [], []
    for i in range(len(alliance_names)):
        if alliance_names[i] == "JetBlue":
            jet_indexes.append(i)
        elif  alliance_names[i] == "Emirates":
            emi_indexes.append(i)
        elif alliance_names[i] == "Turkish":
            tur_indexes.append(i)
        elif alliance_names[i] == "Qantas":
            qan_indexes.append(i)
        elif alliance_names[i] == "Singapore":
            sing_indexes.append(i)
    for d in range(len(departure_date)):
        d1 = "2019-05-01"
        for b in booking_class_code[d]:
            if departure_date[d] < d1:
                jet_references.append(''.join("Pre May 2019"+"-"+b))
            else:
                jet_references.append(''.join("Post May 2019"+"-"+b))
    for r in emi_reference_lst:
        emi_references.append(r)
    for t in tur_reference_lst:
        tur_references.append(t)
    for q in qan_reference_lst:
        qan_references.append(q)
    for dt in range(len(sing_departure_date)):
        dt1 = "2019-07-31"
        if sing_departure_date[dt] < dt1:
            sing_references.append(''.join("Pre July 2019"))
        else:
            sing_references.append(''.join("Post July 2019"))
    return jet_references, jet_indexes, emi_references, emi_indexes, tur_references, tur_indexes, qan_references, qan_indexes, sing_references, sing_indexes


# Function assign discount based on JetBlue reference_list and indices
def jet_tour_code_and_ticket_designator(disc, jet_discount_list, jet_indices_list):
    full_file_path, csv_file_path = read_group_mappings()
    xl = pd.ExcelFile(full_file_path)
    for sheet in xl.sheet_names:
        if sheet == "JetBlue":
            df = pd.read_excel(xl, sheet_name=sheet)
            df.to_csv(csv_file_path, encoding='utf8', index=False)
            df = pd.read_csv(csv_file_path)
            reference_list = df["Reference"].tolist()
    assign_discount(disc, jet_discount_list, jet_indices_list, reference_list, df)
    return disc

# Function assign discount based on Singapore reference_list and indices
def sing_tour_code_and_ticket_designator(disc, sing_discount_list, sing_ctv_reference, sing_indices_list):
    full_file_path, csv_file_path = read_group_mappings()
    xl = pd.ExcelFile(full_file_path)
    for sheet in xl.sheet_names:
        if sheet == "Singapore":
            df = pd.read_excel(xl, sheet_name=sheet)
            df.to_csv(csv_file_path, encoding='utf8', index=False)
            df = pd.read_csv(csv_file_path)
            reference_list = df["Reference"].tolist()
            contract_list = df["Contract"].tolist()
    loc_list = []
    for i, j in zip(sing_discount_list, sing_ctv_reference):
        if i in contract_list and j in reference_list:
            loc = df.loc[(df["Reference"] == j) & (df["Contract"] == i), "Discount"].iloc[0]
            loc_list.append(loc)
    p = dict(zip(sing_indices_list, loc_list))
    m = list(p.values())
    j = list(p.keys())
    for i in range(len(disc)):
        for k in range(len(j)):
            if i == j[k]:
                disc[i] = m[k] 
    return disc

# Function assign discount based on Emirate reference_list and indices
def emi_tour_code_and_ticket_designator(disc, emi_discount_list, emi_indices_list):
    full_file_path, csv_file_path = read_group_mappings()
    xl = pd.ExcelFile(full_file_path)
    for sheet in xl.sheet_names:
        if sheet == "Emirates":
            df = pd.read_excel(xl, sheet_name=sheet)
            df.to_csv(csv_file_path, encoding='utf8', index=False)
            df = pd.read_csv(csv_file_path)
            reference_list = df["Reference"].tolist()
    assign_discount(disc, emi_discount_list, emi_indices_list, reference_list, df)
    return disc


# Function assign discount based on Turkish reference_list and indices
def tur_tour_code_and_ticket_designator(disc, tur_discount_list, tur_indices_list):
    full_file_path, csv_file_path = read_group_mappings()
    xl = pd.ExcelFile(full_file_path)
    for sheet in xl.sheet_names:
        if sheet == "Turkish":
            df = pd.read_excel(xl, sheet_name=sheet)
            df.to_csv(csv_file_path, encoding='utf8', index=False)
            df = pd.read_csv(csv_file_path)
            reference_list = df["Reference"].tolist()
    assign_discount(disc, tur_discount_list, tur_indices_list, reference_list, df)


def qan_tour_code_and_ticket_designator(disc, qan_discount_list, qan_indices_list):
    full_file_path, csv_file_path = read_group_mappings()
    xl = pd.ExcelFile(full_file_path)
    for sheet in xl.sheet_names:
        if sheet == "Qantas":
            df = pd.read_excel(xl, sheet_name=sheet)
            df.to_csv(csv_file_path, encoding='utf8', index=False)
            df = pd.read_csv(csv_file_path)
            reference_list = df["Reference"].tolist()
    assign_discount(disc, qan_discount_list, qan_indices_list, reference_list, df)
    
# End of helper functions


# Create your views here

def home(request):
    return render(request, 'home.html')


# To load raw data from Dropbox
def raw_data(request):
    if request.method == 'POST':
        form = forms.RawdataForm(request.POST)
        # Storing values in session variables
        customer_name = request.POST.get('customer_name')
        request.session['customer_name'] = customer_name
        year = request.POST.get("year")
        request.session['year'] = year
        quarter = request.POST.get("quarter")
        request.session['quarter'] = quarter
        travel_agency = request.POST.get("travel_agency")
        request.session['travel_agency'] = travel_agency
        country = request.POST.get("country")
        request.session['country'] = country

        # Validating the form
        if form.is_valid():
            win_etl_file_path = files_path()
            win_etl_output_file_path = Path(os.path.join(win_etl_file_path, request.POST.get("customer_name")))
            reports_path = Path(os.path.join(win_etl_output_file_path, "3. Performance Reports", year, quarter, "Raw TMC Data-Dev"))
            path = PureWindowsPath(reports_path)

            full_file_name = ''
            for file_name in os.listdir(path):
                if file_name.__contains__("US_"):
                    pass
                elif file_name.__contains__(quarter) and file_name.__contains__(year) and file_name.__contains__(country) and file_name.__contains__("Air") and file_name.__contains__(".xlsx"):
                    full_file_name = os.path.join(path, file_name)
                    new_file_name = customer_name+"_Air_"+quarter+year+".csv"
                    csv_file_full_path = os.path.join(path, new_file_name)
                    request.session['csv_file_path'] = csv_file_full_path
            if full_file_name.__contains__(".xlsx"):
                message = "Found file on this path ::"
                xl = pd.ExcelFile(full_file_name)
                for sheet in xl.sheet_names:
                    df = pd.read_excel(xl, sheet_name=sheet)
                    df.to_csv(csv_file_full_path, encoding='utf8', index=False)
            else:
                message = "File format is not supported. Please check and make sure it is .xlsx"

            context = {'form': form, 'file': full_file_name, 'message': message}

            return render(request, 'get_raw_data.html', context)

    else:
        form = forms.RawdataForm()

    return render(request, 'raw_data.html', {'form': form})


# Function which process raw data to final data
def process_data(request):
    if request.method == 'POST':
        cwd = os.getcwd()
        csv_file_path = request.session['csv_file_path']
        customer_name = request.session['customer_name']
        year = request.session['year']
        quarter = request.session['quarter']
        travel_agency = request.session['travel_agency']
        country = request.session['country']
        # Reading from CSV file
        df = pd.read_csv(csv_file_path)

        # Loading JSON file for column names mappings
        cwd = os.getcwd()
        config_json_file_path = Path(os.path.join(cwd,"static", "json", "config.json"))
        with open(config_json_file_path) as f:
            data = json.load(f)
            mappings = data["CD&R"]

        # Renaming columns with concertiv columns
        del_col_names, del_rows = [], []
        df.rename(columns=mappings, inplace=True)

        # Dropping unnecessary columns
        col_name = df.columns.values.tolist()
        del_col_names = [i for i in col_name if i[0].islower()]
        df.drop(columns=del_col_names, inplace=True, axis=1)

        # Dropping unnecessary rows
        non_airport_codes = ["RTE-2V", "NYP-2V", "SEAAV", "HUD-2V", "WAS-2V", "XXX"]
        for i in non_airport_codes:
            if df["Origin Airport Code"].str.contains(i).any():
                del_rows = (df[df["Origin Airport Code"].str.contains(i)].index.values)
                df.drop(del_rows, axis=0, inplace=True)

        # Loading JSON files
        airport_json_file_path = Path(os.path.join(cwd,"static", "json", "airport.json"))
        with open(airport_json_file_path, encoding="utf8") as p:
            airport_data = json.load(p)

        airline_json_file_path = Path(os.path.join(cwd, "static", "json", "airline.json"))
        with open(airline_json_file_path, encoding="utf8") as l:
            airline_data = json.load(l)

        alliance_json_file_path = Path(os.path.join(cwd, "static", "json", "alliance.json"))
        with open(alliance_json_file_path, encoding="utf8") as m:
            alliance_data = json.load(m)

        # Converting dataframe to list
        airport_ori_code = df["Origin Airport Code"].tolist()
        airport_dest_code = df["Destination Airport Code"].tolist()
        carrier_code = df["Carrier Code"].tolist()

        # Setting rows display
        pd.set_option('display.max_rows', 1500)

        # Forming final dataframe
        df['Departure Date'] = pd.to_datetime(df['Departure Date'], dayfirst=True)
        df.insert(0, "Travel Date Quarter", 'Q' + df['Departure Date'].dt.quarter.astype(str) + " " + df['Departure Date'].dt.year.astype(str), True)
        df.insert(1, "Travel Date Half Year", 'H' + df['Departure Date'].dt.month.gt(6).add(1).astype(str) + " "+df['Departure Date'].dt.year.astype(str), True)
        df.insert(2, "Receive Quarter", quarter + " " + year, True)
        df.insert(3, "Receive Half Year", half_year(quarter) + " " + year, True)
        df.insert(4, "PoS", country, True)
        df.insert(5, "Client", customer_name, True)
        df.insert(6, "Agency", travel_agency, True)
        df.insert(7, "Country", df["Point of Sale"], True)

        df["Carrier Name"] = [v[1] for i in carrier_code for k, v in airline_data.items() if i == k]
        df["Origin City"] = [v[1] for i in airport_ori_code for k, v in airport_data.items() if i == k]
        df["Origin Country"] = ""
        df["Destination City"] = [v[1] for i in airport_dest_code for k, v in airport_data.items() if i == k]
        df["Destination Country"] = ""
        df["International vs. Domestic"] = ""
        df["Refund"] = ""
        df["Exchange"] = ""
        df["Refund / Exchange"] = ""
        df["CTV_Booking Class Code"] = df["Class of Service Code"]
        booking_class_code = df["CTV_Booking Class Code"].tolist()
        df["CTV_Origin_Airport_Id"] = [v[0] for i in airport_ori_code for k, v in airport_data.items() if i == k]
        df["CTV_Destination_Airport_Id"] = [v[0] for i in airport_dest_code for k, v in airport_data.items() if i == k]
        df["CTV_Reference"] = df["Origin Airport Code"] + "-" + df["Destination Airport Code"] + "-" + df["Class of Service Code"]
        df["CTV_Fare"] = df["Class of Service"]
        df["CTV_Carrier_Id"] = [v[0] for i in carrier_code for k, v in airline_data.items() if i == k]
        df["CTV_Alliance_ID"] = [v[3] for i in carrier_code for k, v in airline_data.items() if i == k]
        df["CTV_Alliance_ID"] = df["CTV_Alliance_ID"].astype(str)
        alliance_data_list = df["CTV_Alliance_ID"].tolist()
        df["Errors"] = ""
        df["Savings Alliance Classification"] = [v for i in alliance_data_list for k, v in alliance_data.items() if i == k]

        # Determine savings classifier based on departure_date for JetBlue and Emirates; followed by other airline classifier
        alliance_classification = df["Savings Alliance Classification"].tolist()
        df1 = df.loc[df["Savings Alliance Classification"] == "JetBlue", "Departure Date"]
        df2 = df.loc[df["Savings Alliance Classification"] == "JetBlue", "CTV_Booking Class Code"]
        df3 = df.loc[df["Savings Alliance Classification"] == "Emirates", "CTV_Reference"]
        df4 = df.loc[df["Savings Alliance Classification"] == "Turkish", "CTV_Reference"]
        df5 = df.loc[df["Savings Alliance Classification"] == "Qantas", "CTV_Reference"]
        df6 = df.loc[df["Savings Alliance Classification"] == "Singapore", "Departure Date"]
        df7 = df.loc[df["Savings Alliance Classification"] == "Singapore", "CTV_Reference"]
        df1 = df1.astype(str)
        df2 = df2.astype(str)
        df3 = df3.astype(str)
        df4 = df4.astype(str)
        df5 = df5.astype(str)
        df6 = df6.astype(str)
        df7 = df7.astype(str)
        jet_departure_date = df1.tolist()
        jet_booking_class_code = df2.tolist()
        emi_ctv_reference = df3.tolist()
        tur_ctv_reference = df4.tolist()
        qan_ctv_reference = df5.tolist()
        sing_departure_date = df6.tolist()
        sing_ctv_reference = df7.tolist()
        jet_references, jet_indices, emi_references, emi_indices, tur_references, tur_indices, qan_references, qan_indices, sing_references, sing_indices = savings_classifier(alliance_classification, jet_departure_date, jet_booking_class_code, emi_ctv_reference, tur_ctv_reference, qan_ctv_reference, sing_departure_date)
        df["Departure Date"] = pd.to_datetime(df["Departure Date"]).dt.date
        contract_classifier, jet_discount_list, jet_indexes_list, emi_discount_list, emi_indexes_list, tur_discount_list, tur_indexes_list, disc, qan_discount_list, qan_indexes_list, sing_discount_list, sing_indexes_list, savings_tour_code, savings_ticket_designator = [], [], [], [], [], [], [], [], [], [], [], [], [], []
        for i in range(len(alliance_classification)):
            contract_classifier.append("Not Preferred Airlines")
        for i in range(len(alliance_classification)):
            if alliance_classification[i] == "JetBlue":
                for j in range(len(jet_indices)):
                    contract_classifier[jet_indices[j]] = jet_references[j]
            elif alliance_classification[i] == "Emirates":
                for k in range(len(emi_indices)):
                    contract_classifier[emi_indices[k]] = emi_references[k]
            elif alliance_classification[i] == "Turkish":
                for t in range(len(tur_indices)):
                    contract_classifier[tur_indices[t]] = tur_references[t]
            elif alliance_classification[i] == "Qantas":
                for q in range(len(qan_indices)):
                    contract_classifier[qan_indices[q]] = qan_references[q]
            elif alliance_classification[i] == "Singapore":
                for s in range(len(sing_indices)):
                    contract_classifier[sing_indices[s]] = sing_references[s]
        df["Savings Contract Classifier"] = [j for j in contract_classifier]
        
        # Validating tour code and ticket designator
        contract_discount_classifier = df["Savings Contract Classifier"].tolist()
        for k in range(len(alliance_classification)):
            savings_tour_code.append("Not Preferred Airlines")
            savings_ticket_designator.append("Not Preferred Airlines")
        
        tour_code = df["Tour Code"].tolist()
        ticket_designator = df["Ticket Designator"].tolist()
        df["Tour Code"] = df["Tour Code"].astype(str)
        df["Ticket Designator"] = df["Ticket Designator"].astype(str)
        
        for j in range(len(contract_classifier)):
            disc.append("0")

        # Logic to get discount, tour code and ticket designator for JetBlue
        for i in range(len(jet_indices)):
            if df["Tour Code"].iloc[jet_indices[i]] == "nan" and df["Ticket Designator"].iloc[jet_indices[i]] == "CPO2":
                jet_discount_list.append(contract_discount_classifier[jet_indices[i]])
                jet_indexes_list.append(jet_indices[i])
                savings_tour_code[jet_indices[i]] = "Not Available, Not Matched"
                savings_ticket_designator[jet_indices[i]] = "Available, Matched"
                jet_tour_code_and_ticket_designator(disc, jet_discount_list, jet_indexes_list)
            
            elif df["Tour Code"].iloc[jet_indices[i]] == "CC1103" and df["Ticket Designator"].iloc[jet_indices[i]] == "nan":
                jet_discount_list.append(contract_discount_classifier[jet_indices[i]])
                jet_indexes_list.append(jet_indices[i])
                savings_tour_code[jet_indices[i]] = "Available, Matched"
                savings_ticket_designator[jet_indices[i]] = "Not Available, Not Matched"
                jet_tour_code_and_ticket_designator(disc, jet_discount_list, jet_indexes_list)
                            
            elif df["Tour Code"].iloc[jet_indices[i]] == "CC1103" and df["Ticket Designator"].iloc[jet_indices[i]] != "nan":
                jet_discount_list.append(contract_discount_classifier[jet_indices[i]])
                jet_indexes_list.append(jet_indices[i])
                savings_tour_code[jet_indices[i]] = "Available, Matched"
                if df["Ticket Designator"].iloc[jet_indices[i]] != "CPO2":
                    savings_ticket_designator[jet_indices[i]] = "Available, Not Matched - " + df["Ticket Designator"].iloc[jet_indices[i]]
                else:
                    savings_ticket_designator[jet_indices[i]] = "Available, Matched"
                jet_tour_code_and_ticket_designator(disc, jet_discount_list, jet_indexes_list)

            elif df["Tour Code"].iloc[jet_indices[i]] != "nan" and df["Ticket Designator"].iloc[jet_indices[i]] == "CPO2":
                jet_discount_list.append(contract_discount_classifier[jet_indices[i]])
                jet_indexes_list.append(jet_indices[i])
                if df["Tour Code"].iloc[jet_indices[i]] != "CC1103":
                    savings_tour_code[jet_indices[i]] = "Available, Not Matched - " + df["Tour Code"].iloc[jet_indices[i]]
                else:
                    savings_tour_code[jet_indices[i]] = "Available, Matched"
                savings_ticket_designator[jet_indices[i]] = "Available, Matched"
                jet_tour_code_and_ticket_designator(disc, jet_discount_list, jet_indexes_list)

            elif df["Tour Code"].iloc[jet_indices[i]] == "nan" and df["Ticket Designator"].iloc[jet_indices[i]] == "nan":
                savings_tour_code[jet_indices[i]] = "Not Available, Not Matched"
                savings_ticket_designator[jet_indices[i]] = "Not Available, Not Matched"

            elif df["Tour Code"].iloc[jet_indices[i]] == "nan" and df["Ticket Designator"].iloc[jet_indices[i]] != "CPO2": 
                savings_tour_code[jet_indices[i]] = "Not Available, Not Matched"
                savings_ticket_designator[jet_indices[i]] = "Available, Not Matched -" + df["Ticket Designator"].iloc[jet_indices[i]]

            elif df["Ticket Designator"].iloc[jet_indices[i]] != "CC1103" and df["Ticket Designator"].iloc[jet_indices[i]] == "nan":
                savings_tour_code[jet_indices[i]] = "Available, Not Matched -" + df["Tour Code"].iloc[jet_indices[i]]
                savings_ticket_designator[jet_indices[i]] = "Not Available, Not Matched"

            elif df["Tour Code"].iloc[jet_indices[i]] != "CC1103" and df["Ticket Designator"].iloc[jet_indices[i]] != "CPO2":
                savings_tour_code[jet_indices[i]] = "Available, Not Matched - " + df["Tour Code"].iloc[jet_indices[i]]
                savings_ticket_designator[jet_indices[i]] = "Available, Not Matched - " + df["Ticket Designator"].iloc[jet_indices[i]]
            
        # Logic to get discount, tour code and ticket designator for Emirates    
        for j in range(len(emi_indices)):
            if df["Tour Code"].iloc[emi_indices[j]] == "nan" and df["Ticket Designator"].iloc[emi_indices[j]] == "KBP3":
                emi_discount_list.append(contract_discount_classifier[emi_indices[j]])
                emi_indexes_list.append(emi_indices[j])
                savings_tour_code[emi_indices[j]] = "Not Available, Not Matched"
                savings_ticket_designator[emi_indices[j]] = "Available, Matched"
                emi_tour_code_and_ticket_designator(disc, emi_discount_list, emi_indexes_list)
                    
            elif df["Tour Code"].iloc[emi_indices[j]] == "ZZKBP3ZZ" and df["Ticket Designator"].iloc[emi_indices[j]] == "nan":
                emi_discount_list.append(contract_discount_classifier[emi_indices[j]])
                emi_indexes_list.append(emi_indices[j])
                savings_tour_code[emi_indices[j]] = "Available, Matched"
                savings_ticket_designator[emi_indices[j]] = "Not Available, Not Matched"
                emi_tour_code_and_ticket_designator(disc, emi_discount_list, emi_indexes_list)
            
            elif df["Tour Code"].iloc[emi_indices[j]] == "ZZKBP3ZZ" and df["Ticket Designator"].iloc[emi_indices[j]] != "nan":
                emi_discount_list.append(contract_discount_classifier[emi_indices[j]])
                emi_indexes_list.append(emi_indices[j])
                savings_tour_code[emi_indices[j]] = "Available, Matched"
                if df["Ticket Designator"].iloc[emi_indices[j]] != "KBP3":
                    savings_ticket_designator[emi_indices[j]] = "Available, Not Matched - " + df["Ticket Designator"].iloc[emi_indices[j]]
                else:
                    savings_ticket_designator[emi_indices[j]] = "Available, Matched"
                emi_tour_code_and_ticket_designator(disc, emi_discount_list, emi_indexes_list)

            elif (df["Tour Code"].iloc[emi_indices[j]] != "nan" or df["Tour Code"].iloc[emi_indices[j]] != "ZZKBP3ZZ") and df["Ticket Designator"].iloc[emi_indices[j]] == "KBP3":
                emi_discount_list.append(contract_discount_classifier[emi_indices[j]])
                emi_indexes_list.append(emi_indices[j])
                savings_tour_code[emi_indices[j]] = "Available, Not Matched - " + df["Tour Code"].iloc[emi_indices[j]]
                savings_ticket_designator[emi_indices[j]] = "Available, Matched"
                emi_tour_code_and_ticket_designator(disc, emi_discount_list, emi_indexes_list)

            elif df["Tour Code"].iloc[emi_indices[j]] == "nan" and df["Ticket Designator"].iloc[emi_indices[j]] == "nan":
                savings_tour_code[emi_indices[j]] = "Not Available, Not Matched"
                savings_ticket_designator[emi_indices[j]] = "Not Available, Not Matched"

            elif df["Tour Code"].iloc[emi_indices[j]] == "nan" and df["Ticket Designator"].iloc[jet_indices[j]] != "KBP3": 
                savings_tour_code[emi_indices[j]] = "Not Available, Not Matched"
                savings_ticket_designator[emi_indices[j]] = "Available, Not Matched -" + df["Ticket Designator"].iloc[emi_indices[j]]

            elif df["Tour Code"].iloc[emi_indices[j]] != "ZZKBP3ZZ" and df["Ticket Designator"].iloc[emi_indices[j]] == "nan":
                savings_tour_code[emi_indices[j]] = "Available, Not Matched -" + df["Tour Code"].iloc[emi_indices[j]]
                savings_ticket_designator[emi_indices[j]] = "Not Available, Not Matched"

            elif df["Tour Code"].iloc[emi_indices[j]] != "ZZKBP3ZZ" and df["Ticket Designator"].iloc[emi_indices[j]] != "KBP3":
                savings_tour_code[emi_indices[j]] = "Available, Not Matched - " + df["Tour Code"].iloc[emi_indices[j]]
                savings_ticket_designator[emi_indices[j]] = "Available, Not Matched - " + df["Ticket Designator"].iloc[emi_indices[j]]
            
        
        # Logic to get discount, tour code and ticket designator for Turkish
        for t in range(len(tur_indices)):
            if df["Tour Code"].iloc[tur_indices[t]] == "nan" and df["Ticket Designator"].iloc[tur_indices[t]] == "FS09":
                tur_discount_list.append(contract_discount_classifier[tur_indices[t]])
                tur_indexes_list.append(tur_indices[t])
                savings_tour_code[tur_indices[t]] = "Not Available, Not Matched"
                savings_ticket_designator[tur_indices[t]] = "Available, Matched"
                tur_tour_code_and_ticket_designator(disc, tur_discount_list, tur_indexes_list)
                    
            elif df["Tour Code"].iloc[tur_indices[t]] == "CCC79751" and df["Ticket Designator"].iloc[tur_indices[t]] == "nan":
                tur_discount_list.append(contract_discount_classifier[tur_indices[t]])
                tur_indexes_list.append(tur_indices[t])
                savings_tour_code[tur_indices[t]] = "Available, Matched"
                savings_ticket_designator[tur_indices[t]] = "Not Available, Not Matched"
                tur_tour_code_and_ticket_designator(disc, tur_discount_list, tur_indexes_list)
            
            elif df["Tour Code"].iloc[tur_indices[t]] == "CCC79751" and df["Ticket Designator"].iloc[tur_indices[t]] != "nan":
                tur_discount_list.append(contract_discount_classifier[tur_indices[t]])
                tur_indexes_list.append(tur_indices[t])
                savings_tour_code[tur_indices[t]] = "Available, Matched"
                if df["Ticket Designator"].iloc[tur_indices[t]] != "FS09":
                    savings_ticket_designator[tur_indices[t]] = "Available, Not Matched - " + df["Ticket Designator"].iloc[tur_indices[t]]
                else:
                    savings_ticket_designator[tur_indices[t]] = "Available, Matched"
                tur_tour_code_and_ticket_designator(disc, tur_discount_list, tur_indexes_list)

            elif df["Ticket Designator"].iloc[tur_indices[t]] != "nan"  and df["Ticket Designator"].iloc[tur_indices[t]] == "FS09":
                tur_discount_list.append(contract_discount_classifier[tur_indices[t]])
                tur_indexes_list.append(tur_indices[t])
                if df["Tour Code"].iloc[tur_indices[t]] != "CCC79751":
                    savings_tour_code[tur_indices[t]] = "Available, Not Matched - " + df["Tour Code"].iloc[tur_indices[t]]
                else:
                    savings_tour_code[tur_indices[t]] = "Available, Matched"
                savings_ticket_designator[tur_indices[t]] = "Available, Matched"
                tur_tour_code_and_ticket_designator(disc, tur_discount_list, tur_indexes_list)

            elif df["Tour Code"].iloc[tur_indices[t]] == "nan" and df["Ticket Designator"].iloc[tur_indices[t]] == "nan":
                savings_tour_code[tur_indices[t]] = "Not Available, Not Matched"
                savings_ticket_designator[tur_indices[t]] = "Not Available, Not Matched"

            elif df["Tour Code"].iloc[tur_indices[t]] == "nan" and df["Ticket Designator"].iloc[tur_indices[t]] != "FS09": 
                savings_tour_code[tur_indices[t]] = "Not Available, Not Matched"
                savings_ticket_designator[tur_indices[t]] = "Available, Not Matched -" + df["Ticket Designator"].iloc[tur_indices[t]]

            elif df["Tour Code"].iloc[tur_indices[t]] != "CCC79751" and df["Ticket Designator"].iloc[tur_indices[t]] == "nan":
                savings_tour_code[tur_indices[t]] = "Available, Not Matched -" + df["Tour Code"].iloc[tur_indices[t]]
                savings_ticket_designator[tur_indices[t]] = "Not Available, Not Matched"

            elif df["Tour Code"].iloc[tur_indices[t]] != "CCC79751" and df["Ticket Designator"].iloc[tur_indices[t]] != "FS09":
                savings_tour_code[tur_indices[t]] = "Available, Not Matched - " + df["Tour Code"].iloc[tur_indices[t]]
                savings_ticket_designator[tur_indices[t]] = "Available, Not Matched - " + df["Ticket Designator"].iloc[tur_indices[t]]
            
        # Logic to get discount, tour code and ticket designator for Qantas
        for q in range(len(qan_indices)):
            if df["Tour Code"].iloc[qan_indices[q]] == "BOT":
                qan_discount_list.append(contract_discount_classifier[qan_indices[q]])
                qan_indexes_list.append(qan_indices[q])
                savings_tour_code[qan_indices[q]] = "Available, Matched"
                savings_ticket_designator[qan_indices[q]] = "Not Applicable"
                qan_tour_code_and_ticket_designator(disc, qan_discount_list, qan_indexes_list)

            elif df["Tour Code"].iloc[qan_indices[t]] != "BOT":
                qan_discount_list.append(contract_discount_classifier[qan_indices[q]])
                qan_indexes_list.append(qan_indices[q])
                savings_tour_code[qan_indices[q]] = "Available, Not Matched - " + df["Tour Code"].iloc[qan_indices[q]]
                savings_ticket_designator[qan_indices[q]] = "Not Applicable"
                qan_tour_code_and_ticket_designator(disc, qan_discount_list, qan_indexes_list)

            elif df["Tour Code"].iloc[qan_indices[q]] == "nan":
                savings_tour_code[qan_indices[q]] = "Not Available, Not Matched"
                savings_ticket_designator[qan_indices[q]] = "Not Applicable"
        
        # Logic to get discount, tour code and ticket designator for Singapore
        for s in range(len(sing_indices)):
            if df["Tour Code"].iloc[sing_indices[s]] == "nan" and df["Ticket Designator"].iloc[sing_indices[s]] == "CDM3":
                sing_discount_list.append(contract_discount_classifier[sing_indices[s]])
                sing_indexes_list.append(sing_indices[s])
                savings_tour_code[sing_indices[s]] = "Not Available, Not Matched"
                savings_ticket_designator[sing_indices[s]] = "Available, Matched"
                sing_tour_code_and_ticket_designator(disc, sing_discount_list, sing_ctv_reference,sing_indexes_list)
            
            elif df["Tour Code"].iloc[sing_indices[s]] == "A74PH" and df["Ticket Designator"].iloc[sing_indices[s]] == "nan":
                sing_discount_list.append(contract_discount_classifier[sing_indices[s]])
                sing_indexes_list.append(sing_indices[s])
                savings_tour_code[sing_indices[s]] = "Available, Matched"
                savings_ticket_designator[sing_indices[s]] = "Not Available, Not Matched"
                sing_tour_code_and_ticket_designator(disc, sing_discount_list, sing_ctv_reference, sing_indexes_list)
                            
            elif df["Tour Code"].iloc[sing_indices[s]] == "A74PH" and df["Ticket Designator"].iloc[sing_indices[s]] != "nan":
                sing_discount_list.append(contract_discount_classifier[sing_indices[s]])
                sing_indexes_list.append(sing_indices[s])
                savings_tour_code[sing_indices[s]] = "Available, Matched"
                if df["Ticket Designator"].iloc[sing_indices[s]] != "CDM3":
                    savings_ticket_designator[sing_indices[s]] = "Available, Not Matched - " + df["Ticket Designator"].iloc[sing_indices[s]]
                else:
                    savings_ticket_designator[sing_indices[s]] = "Available, Matched"
                sing_tour_code_and_ticket_designator(disc, sing_discount_list, sing_ctv_reference, sing_indexes_list)

            elif df["Tour Code"].iloc[sing_indices[s]] != "nan" and df["Ticket Designator"].iloc[sing_indices[s]] == "CDM3":
                sing_discount_list.append(contract_discount_classifier[sing_indices[s]])
                sing_indexes_list.append(sing_indices[s])
                if df["Tour Code"].iloc[sing_indices[s]] != "A74PH":
                    savings_tour_code[sing_indices[s]] = "Available, Not Matched - " + df["Tour Code"].iloc[sing_indices[s]]
                else:
                    savings_tour_code[sing_indices[s]] = "Available, Matched"
                savings_ticket_designator[sing_indices[s]] = "Available, Matched"
                sing_tour_code_and_ticket_designator(disc, sing_discount_list, sing_ctv_reference, sing_indexes_list)

            elif df["Tour Code"].iloc[sing_indices[s]] == "nan" and df["Ticket Designator"].iloc[sing_indices[s]] == "nan":
                savings_tour_code[sing_indices[s]] = "Not Available, Not Matched"
                savings_ticket_designator[sing_indices[s]] = "Not Available, Not Matched"

            elif df["Tour Code"].iloc[sing_indices[s]] == "nan" and df["Ticket Designator"].iloc[sing_indices[s]] != "CDM3": 
                savings_tour_code[sing_indices[s]] = "Not Available, Not Matched"
                savings_ticket_designator[sing_indices[s]] = "Available, Not Matched -" + df["Ticket Designator"].iloc[sing_indices[s]]

            elif df["Ticket Designator"].iloc[sing_indices[s]] != "A74PH" and df["Ticket Designator"].iloc[sing_indices[s]] == "nan":
                savings_tour_code[sing_indices[s]] = "Available, Not Matched -" + df["Tour Code"].iloc[sing_indices[s]]
                savings_ticket_designator[sing_indices[s]] = "Not Available, Not Matched"

            elif df["Tour Code"].iloc[sing_indices[s]] != "A74PH" and df["Ticket Designator"].iloc[sing_indices[s]] != "CDM3":
                savings_tour_code[sing_indices[s]] = "Available, Not Matched - " + df["Tour Code"].iloc[sing_indices[s]]
                savings_ticket_designator[sing_indices[s]] = "Available, Not Matched - " + df["Ticket Designator"].iloc[sing_indices[s]]
        
        df["Tour Code"] = [tc for tc in tour_code]
        df["Ticket Designator"] = [td for td in ticket_designator]
        df["Contract Classifier Tour Code"] = [tc for tc in savings_tour_code]
        df["Contract Classifier Ticket Designator"] = [td for td in savings_ticket_designator]
        df["Discount"] = [d for d in disc]
        pre_dis, pre, sav = [], [], []
        df["Fare"] = df["Fare"].astype(float)
        df["Fare"] = df["Fare"].round(2)
        discount_applied = []
        classifier_tour_code = df["Contract Classifier Tour Code"].tolist()
        classifier_ticket_designator = df["Contract Classifier Ticket Designator"].tolist()
        for ctc, ctd in zip(classifier_tour_code, classifier_ticket_designator):
            if ctc == "Available, Matched" or ctd == "Available, Matched":
                discount_applied.append("Y")
            else:
                discount_applied.append("N")
        df["If Discount Applied"] = [da for da in discount_applied]
        df["Discount"] = df["Discount"].astype(float)
        df["Discount"] = df["Discount"].round(2)
        fare = df["Fare"].tolist()
        discount = df["Discount"].tolist()
        for d in discount:
            pre.append(1 - d)
        for f, d in zip(fare, pre):
            pre_dis.append(f / d)
        df["Pre-Discount Cost"] = [pr for pr in pre_dis]
        df["Pre-Discount Cost"] = df["Pre-Discount Cost"].round(2)
        pre_disc_cost = df["Pre-Discount Cost"].tolist()
        for f, pre in zip(fare, pre_disc_cost):
            sav.append(pre - f)
        df["Savings"] = [s for s in sav]
        df["Savings"] = df["Savings"].round(2)
        non_prism = []
        group_deals = ["JetBlue", "Qantas", "Turkish", "Singapore", "Emirates", "Cathay"]
        prism_airlines = ["American / Oneworld", "United / Star Alliance"]
        for ali in range(len(alliance_classification)):
            non_prism.append("Y")
            if alliance_classification[ali] in group_deals:
                non_prism[ali] = "N" 
        df["Non-Prism Preferred"] = [np for np in non_prism]

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
                   "If Discount Applied", "Discount", "Pre-Discount Cost", "Savings", "Non-Prism Preferred"]
        
        df = df.reindex(columns=headers)

        # Gethering information to get details from Prism airlines
        quarter_year = quarter + " " + year
        win_etl_file_path = files_path()
        new_file_path = Path(os.path.join(win_etl_file_path, customer_name, "3. Performance Reports", year, quarter, "Raw TMC Data-Dev"))
        prism_file_name = "Air PRISM & Other.xlsx"
        csv_prism_file_name = "Air PRISM & Other.csv"
        file_path = Path(os.path.join(new_file_path, prism_file_name))
        csv_file_path = Path(os.path.join(new_file_path, csv_prism_file_name))
        
        prism_airlines_disc = get_prism_airline_info(file_path, csv_file_path, quarter_year, prism_airlines)
        n = 4
        prism_airlines_disc_list = [prism_airlines_disc[i * n:(i+1)*n] for i in range((len(prism_airlines_disc) + n - 1) // n)]
        l1, l2, l3 = list(), list(), list()
        for p in range(len(prism_airlines)):
            x = df.index[df["Savings Alliance Classification"] == prism_airlines[p]].tolist()
            vol = len(x)/len(df.index)
            vol = vol * 100
            p_vol = str(round(vol, 2)) + "%"
            l1.append(p_vol)
            prism_sum_savings = float(prism_airlines_disc_list[p][2])
            prism_sum_pre_discount = float(prism_airlines_disc_list[p][1])
            net = (prism_sum_savings/prism_sum_pre_discount)*100
            prism_airlines_disc_list[p][2] = "$" + str(prism_airlines_disc_list[p][2])
            prism_airlines_disc_list[p][1] = "$" + str(prism_airlines_disc_list[p][1])
            p_net = str(round(net, 2)) + "%"
            l2.append(p_net)
            l3.append(prism_airlines_disc_list[p][3])
        for pa, i, j, k in zip(prism_airlines_disc_list, l1, l2, l3):
            pa.insert(3, i)
            pa.insert(5, j)
            pa.insert(6, k)
        
        # Writing new column names into separate .xlsx file
        win_etl_file_path = files_path()
        new_file_path = Path(os.path.join(win_etl_file_path, customer_name, "3. Performance Reports", year, quarter, "Raw TMC Data-Dev"))
        new_file_name = customer_name+"_Air_"+quarter+year+"_FinalData"+".xlsx"
        file_name = Path(os.path.join(new_file_path, new_file_name))
        df.to_excel(file_name, encoding='utf8', index=False)
        
        # Final savings report for Q1 2022 on quaterly basis
        jet_blue_list, emi_list = [], []
        jet_blue_list.append("JetBlue")
        sum_jet_pre_dis_cost = df.loc[df["Savings Alliance Classification"] == "JetBlue", "Pre-Discount Cost"].sum()
        jet_pre_dis_cost = "$" + str(round(sum_jet_pre_dis_cost,2))
        jet_blue_list.append(jet_pre_dis_cost)
        sum_jet_fare = df.loc[df["Savings Alliance Classification"] == "JetBlue", "Fare"].sum()
        jet_fare = "$" + str(round(sum_jet_fare, 2))
        jet_blue_list.append(jet_fare)
        vol = len(jet_indices)/len(df.index)
        vol = (vol*100)
        jet_vol = str(round(vol, 2)) + "%"
        jet_blue_list.append(jet_vol)
        sum_jet_savings = df.loc[df["Savings Alliance Classification"] == "JetBlue", "Savings"].sum()
        jet_savings = "$" + str(round(sum_jet_savings, 2))
        jet_blue_list.append(jet_savings)
        net = (sum_jet_savings / sum_jet_pre_dis_cost)*100
        jet_net = str(round(net, 2)) + "%"
        jet_blue_list.append(jet_net)
        sum_savings = df["Savings"].sum()
        savings = "$" + str(round(sum_savings, 2))
        jet_blue_list.append(savings)

        emi_list.append("Emirates")
        sum_emi_pre_dis_cost = df.loc[df["Savings Alliance Classification"] == "Emirates", "Pre-Discount Cost"].sum()
        emi_pre_dis_cost = "$" + str(round(sum_emi_pre_dis_cost, 2))
        emi_list.append(emi_pre_dis_cost)
        sum_emi_fare = df.loc[df["Savings Alliance Classification"] == "Emirates", "Fare"].sum()
        emi_fare = "$" + str(round(sum_emi_fare, 2))
        emi_list.append(emi_fare)
        vol = len(emi_indices)/len(df.index)
        vol = (vol*100)
        emi_vol = str(round(vol,2)) + "%"
        emi_list.append(emi_vol)
        sum_emi_savings = df.loc[df["Savings Alliance Classification"] == "Emirates", "Savings"].sum()
        emi_savings = "$" + str(round(sum_emi_savings,2))
        emi_list.append(emi_savings)
        net = (sum_emi_savings / sum_emi_pre_dis_cost)*100
        emi_net = str(round(net,2)) + "%"
        emi_list.append(emi_net)
        emi_list.append(savings)
        
        table = {"jet_blue_list": jet_blue_list, "emi_list": emi_list, "prism_list": prism_airlines_disc_list}
        for i in prism_airlines_disc_list:
            for j in i:
                if j.isalpha():
                    pass
                elif j.isalpha() and j.__contains__("%"):
                    sum = sum + j
                    print(sum)
        # prism_pre_discount_sum = 0
        # for i in range(len(prism_airlines_disc_list)):
        #     for j in prism_airlines_disc_list[i]:
        #         print(j)
                # convert_prism_pre_discount = int(prism_airlines_disc_list[i][j][1])
                # prism_pre_discount_sum += convert_prism_pre_discount
        # print(prism_pre_discount_sum)
        # Values to populate on graphs
        final_pre_discount = sum_jet_pre_dis_cost + sum_emi_pre_dis_cost
        request.session['final_pre_discount'] = final_pre_discount
        final_savings = sum_jet_savings + sum_emi_savings
        request.session['final_savings'] = final_savings
        actual_spend = sum_jet_fare + sum_emi_fare
        request.session['actual_spend'] = actual_spend

        # Deleting previous version of CSV - raw data file
        os.chdir(new_file_path)
        pre_csv_file = customer_name+"_Air_"+quarter+year+".csv"
        if os.path.exists(pre_csv_file):
            os.remove(pre_csv_file)

        # Deleting air_prism file
        air_prism_file = Path(os.path.join(new_file_path, "Air PRISM & Other.csv"))
        if os.path.exists(air_prism_file):
            os.remove(air_prism_file)

        # Deleting CSV file of Group mappings
        username = os.getlogin()
        user_path = Path(os.path.join("C:/Users", username))
        group_deals_path = Path(os.path.join(user_path, "Dropbox (Concertiv)", "Ve Arc Sharing", "Group Airline Discount Mapping", "Group Airline Discounts"))
        path = PureWindowsPath(group_deals_path)
        csv_file_path = Path(os.path.join(path, "Group Airline Discounts Mapping.csv"))
        os.chdir(path)
        if os.path.exists(csv_file_path):
            os.remove(csv_file_path)

    os.chdir(cwd)
    context={'table': table}
    return render(request, 'process_data.html', context)

# Displaying DataFrame in Graphs using Charts.js
def get_graphs(request):
    final_pre_discount = request.session['final_pre_discount']
    final_savings = request.session['final_savings']
    actual_spend = request.session['actual_spend']
    data = {"prediscount": final_pre_discount, "savings": final_savings, "spend": actual_spend}
    context={'graph':data}
    return render(request, 'get_graphs.html', context)
