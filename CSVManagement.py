from datetime import datetime
from PySide6.QtCore import QTimer
import csv
import os
import pandas as pd
import Common
import CostCell

class CSVManagement:
    def __init__(self, username, data_2d_list):
        self.username = username
        self.file_name = self.generate_file_name()
        self.data_2d_list = data_2d_list
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.save_to_csv) #Automatic saving to csv. See below function.
        self.auto_save_timer.start(30000) #saves every 39 seconds

    def generate_file_name(self):
        current_date = datetime.now()
        return f"cost_tracking_app_{self.username}_{current_date.year}_{current_date.month}.csv"

    def save_to_csv(self, save_directory=None):
        folder_path = save_directory if save_directory else Common.default_directory
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, self.file_name)

        if not os.path.exists(file_path):
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Date'] + CostCell.CostCellUI.headerlabels)

        try:
            with open(file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(self.data_2d_list)
            print("Data saved automatically.", file_path)
        except Exception as e:
            print(f"Error saving data: {e}")

    def start_new_csv_for_month(self):
        self.file_name = self.generate_file_name()
        initial_column_count = len(self.data_2d_list[0])
        self.data_2d_list = [["" for _ in range(initial_column_count)] for _ in range(len(self.data_2d_list))]
        self.save_to_csv()    
        
    def new_month_check(self):
        if self.data_2d_list and self.data_2d_list[-1] and self.data_2d_list[-1][-1] :
            last_date_str = self.data_2d_list[-1][-1]
            last_date_in_table = datetime.strptime(last_date_str, "%d %B %Y").date()
            current_date = datetime.now().date()
            if last_date_in_table.month != current_date.month:
                self.start_new_csv_for_month()

    def previous_months_check(self):
        csv_files = []
        for file in os.listdir(Common.default_directory):
            if file.endswith(".csv") and file.startswith(self.username):
                csv_files.append(file)
            return csv_files
        
    def csv_data_load(self, filename):
        full_path = os.path.join(Common.default_directory, filename)
        with open(full_path, 'r') as file:
            reader = csv.reader(file)
            self.data_2d_list = list(reader)