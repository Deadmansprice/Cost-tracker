#linked to main. Do not remove that file. This file is for putting in various classes for different windows.
import pandas as pd
from datetime import datetime
from pathlib import Path
from Common import CSV_FILENAME, get_file_paths
import CostCell
import UserManagement

class DataManager:
    def __init__(self, username):
        self.username = username

    def create_monthly_csv(self, default_directory):
        today = datetime.now()
        month_suffix = today.strftime('%Y_%m')
        _, csv_file_path = get_file_paths(default_directory, self.username)
        return csv_file_path

    def get_current_month_csv(self):
        today = datetime.now()
        month_suffix = today.strftime('%Y_%m')


    def create_empty_csv(self):
        try:
            today = datetime.now().strftime("%d %B %Y")
            columns = [today]
            cf = pd.DataFrame(columns=columns)
            cf.to_csv(CSV_FILENAME, index=False)
        except Exception as e:
            print(f"An error occured while creating the CSV file: {e}")

    def check_file_exists(self, file_path):
        return Path(file_path).exists()


#It's for returning functions as being used by main.py
class Returner:
    @staticmethod
    def create_user_management():
        return UserManagement.UserManagement()
    
    @staticmethod
    def create_cost_cell(username):
        return CostCell(username)