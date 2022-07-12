from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, View
from .forms import *
from .models import *

from pathlib import Path, PureWindowsPath
import os
import json
import pandas as pd

# Create your views here.
class BasicView(View):
    def files_path(self):
        cwd = os.getcwd()
        config_json_file_path = Path(os.path.join(cwd,"static", "json", "config.json"))
        with open(config_json_file_path) as f:
            data = json.load(f)
        username = os.getlogin()
        user_path = Path(os.path.join("C:/Users", username))
        elt_file_path = data["win_etl_output_files_path"]
        win_etl_file_path = Path(os.path.join(user_path, elt_file_path))
        return win_etl_file_path

class HomeView(TemplateView):
    template_name = 'home.html'

class RawDataView(BasicView):
    template_name = 'air/raw_data.html'
    form_class = RawdataForm

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        customer_name = request.POST.get('customer_name')
        travel_agency = request.POST.get('travel_agency')
        quarter = request.POST.get('quarter')
        year = request.POST.get('year')
        country = request.POST.get('country')
        context = {}
        
        if form.is_valid():
            win_etl_file_path = self.files_path()
            win_etl_output_file_path = Path(os.path.join(win_etl_file_path, request.POST.get("customer_name")))
            reports_path = Path(os.path.join(win_etl_output_file_path, "3. Performance Reports", year, quarter, "Raw TMC Data-Dev"))
            path = PureWindowsPath(reports_path)
            file_path = ''
            for file_name in os.listdir(path):
                if not file_name.startswith(customer_name):
                    pass
                elif file_name.startswith(customer_name) and file_name.__contains__("Air")and file_name.__contains__(quarter) and file_name.__contains__(year) and file_name.__contains__(country) and file_name.__contains__(".xlsx"):                 
                    file_path = os.path.join(path, file_name)
                    csv_file_path = customer_name + "_Air_" + quarter + year + ".csv"
                    message = "Found the file. Click below to process the file"
                else:
                    message = "File not found. Please check the path and Try again."
            context = {'form': form,'file_path': file_path, 'message': message}
            return render(request, 'air/get_raw_data.html', context)
        return render(request, self.template_name, {'form': form})


class ProcessDataView(BasicView):
    template_name = 'air/process_data.html'


    def post(self, request, *args, **kwargs):
        print("Processing data...")
    
