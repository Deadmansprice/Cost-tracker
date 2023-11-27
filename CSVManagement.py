##### - CSVManagement.py:
from datetime import datetime
from PySide6.QtCore import QTimer
import csv
import os
import pandas as pd
import Common
import CostCell
from pathlib import Path
import UserManagement
import platform

class CSVManagement:
    def __init__(self, username, data_2d_list, headerlabels):
        self.username = username
        self.default_directory = Common.get_current_directory()
        self.file_name = os.path.join(Common.default_directory, self.generate_file_name())
        self.data_2d_list = data_2d_list
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.save_to_csv) #Automatic saving to csv. See below function.
        self.auto_save_timer.start(30000) #saves every 30 seconds

    def generate_file_name(self):
        current_date = datetime.now()
        file_name = f"cost_tracking_app_{self.username}_{current_date.year}_{current_date.month}.csv"
        return os.path.join(self.default_directory, file_name)
    
    def create_empty_csv(self):
        if not os.path.exists(self.file_name):
            print("Creating new CSV file at:", self.file_name)
            with open(self.file_name, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Date"] + Common.headerlabels)

    #Header update. checks the local system for date/time and sees if it's current month, if the month has passed then it will create a new file for that newly-current month.
    def update_headers(self):
        self.new_month_check()
        current_date = datetime.now()
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        if not os.path.isfile(self.file_name):
            self.create_empty_csv()
        formatted_date = current_date.strftime("%-d %B %Y") if platform.system() != 'Windows' else current_date.strftime("%#d %B %Y")

        with open(self.file_name,'r', newline='') as file:
            reader = csv.reader(file)
            data = list(reader)

        if formatted_date not in data[0]:
            data[0].append(formatted_date)

            with open (self.file_name, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)
        
    def save_to_csv(self, save_directory=None):
        file_path = self.file_name

        if not os.path.exists(file_path):
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Date'] + Common.headerlabels)
        
        save_path = save_directory if save_directory else file_path
        with open(file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.data_2d_list)
            print("Data saved automatically.", save_path)

    def start_new_csv_for_month(self):
        self.file_name = self.generate_file_name()
        initial_column_count = len(self.data_2d_list[0])
        self.data_2d_list = [["" for _ in range(initial_column_count)] for _ in range(len(self.data_2d_list))]
        self.save_to_csv()    
        
    def new_month_check(self):
        current_date = datetime.now().date()
        if self.data_2d_list:
            last_date_str = self.data_2d_list[-1][0]
            last_date_in_table = datetime.strptime(last_date_str, "%d %B %Y").date()
            if last_date_in_table.month != current_date.month:
                self.start_new_csv_for_month()

    def previous_months_check(self):
        csv_files = []
        for file in os.listdir(Common.default_directory):
            if file.endswith(".csv") and file.startswith(self.username):
                csv_files.append(file)
        return csv_files
        
    def csv_data_load(self, file_name):
        full_path = os.path.join(self.default_directory, file_name)
        print("Loading CSV data from:", full_path)
        if not os.path.exists(full_path):
            return []
        with open(full_path, 'r') as file:
            reader = csv.reader(file)
            self.data_2d_list = list(reader)
