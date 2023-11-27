##### - Common.py:
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QInputDialog
import CostCell
import Common
import UserManagement
import CSVManagement
from pathlib import Path
import os
import json

home_directory = os.path.expanduser('~') #Grabs user's own home directory
default_directory = os.path.join(home_directory, "Cost Tracker", "Cost Tracking Data")
headerlabels = ['Food', 'Fuel', 'Bills', 'Investments', 'Miscellaneous']
#Variables to be used by all the files to keep it dynamic. Necessary when wrking with multiple files.

JSON_FILENAME = ""
FOLDER_PATH_FILENAME = ""
CSV_FILENAME = ""

def update_file_paths():
    global JSON_FILENAME, CSV_FILENAME, FOLDER_PATH_FILENAME
    JSON_FILENAME = os.path.join(default_directory, "login_data.json")
    CSV_FILENAME = os.path.join(default_directory, "cost_tracking_app.csv")
    FOLDER_PATH_FILENAME = os.path.join(default_directory, "folder_path.json")

update_file_paths()

#Central folder path
def get_current_directory():
    folder_path = load_folder_path()
    return folder_path if folder_path else default_directory

def save_current_directory(folder_path):
    os.makedirs(os.path.dirname(FOLDER_PATH_FILENAME), exist_ok=True)
    with open(FOLDER_PATH_FILENAME, "w") as f:
        json.dump({"folder_path": folder_path}, f)

def load_folder_path():
    if os.path.isfile(FOLDER_PATH_FILENAME):
        with open(FOLDER_PATH_FILENAME, "r") as f:
            data = json.load(f)
            return data.get("folder_path")
    return ""

#Creation of user data upon first launch
def create_user_data(username, password, data_2d_list=[]):       
    user_management = UserManagement.UserManagement()
    json_file_path, csv_file_path =  get_file_paths(get_current_directory(), username)
    hashed_password = user_management.hash_password(password)
    user_management.login_data[username] = hashed_password
    
    user_management.save_login_data()
    csv_manager = CSVManagement.CSVManagement(username, data_2d_list, headerlabels)
    csv_manager.create_empty_csv()
    
def update_default_directory(new_directory):
    global default_directory
    save_current_directory(new_directory)
    default_directory = get_current_directory()
    update_file_paths()
    print("Updated default directory to:", default_directory)
    # Notify other modules or components of the change if necessary

#Checks for file paths.
def get_file_paths(default_directory, username):
    json_file_path = f"{default_directory}/login_data_{username}.json"
    csv_file_path =  f"{default_directory}/cost_tracking_{username}.csv"
    return json_file_path, csv_file_path

#Reference to main.py. 
class user_list_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cost Tracker")
        self.user_management = UserManagement.UserManagement()
        self.login_data = self.user_management.load_login_data()

        self.layout = QVBoxLayout()

        for username in self.login_data.keys():
            button = QPushButton(username)
            button.clicked.connect(lambda checked=False, u=username: self.password_check(u))
            self.layout.addWidget(button)
            

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def password_check(self,username):
        password, ok = QInputDialog.getText(self, "Password", f"Enter password for {username}:")
        if ok:
            is_valid = self.user_management.validate_password(username, password)
            if is_valid:
                self.close()
                self.CostCell_window = CostCell.CostCell(username)
                self.CostCell_window.show()