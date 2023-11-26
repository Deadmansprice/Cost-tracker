##### - Common.py:
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QInputDialog
import CostCell
import Common
import UserManagement
import CSVManagement
from pathlib import Path
import os

home_directory = os.path.expanduser('~') #Grabs user's own home directory
default_directory = os.path.join(home_directory, "Cost Tracker", "Cost Tracking Data")
headerlabels = ['Food', 'Fuel', 'Bills', 'Investments', 'Miscellaneous']
#Variables to be used by all the files to keep it dynamic. Necessary when wrking with multiple files.

JSON_FILENAME = os.path.join(default_directory, "login_data.json")
FOLDER_PATH_FILENAME = os.path.join(default_directory,"folder_path.json")
CSV_FILENAME = os.path.join(default_directory,"cost_tracking_app.csv")

#Creation of user data upon first launch
def create_user_data(username, password, default_directory, data_2d_list=[]):
    if default_directory is None:
        default_directory = FOLDER_PATH_FILENAME

    tracking_data_folder = Path(default_directory, "Cost Tracking Data")
    tracking_data_folder.mkdir(parents=True, exist_ok=True)
        
    user_management = UserManagement.UserManagement()
    json_file_path, csv_file_path =  get_file_paths(default_directory, username)
    hashed_password = user_management.hash_password(password)
    user_management.login_data[username] = hashed_password
    
    user_management.save_login_data()
    csv_manager = CSVManagement.CSVManagement(username, [], Common.headerlabels)
    
def update_default_directory(new_directory):
    global default_directory, JSON_FILENAME, CSV_FILENAME, FOLDER_PATH_FILENAME
    default_directory = new_directory

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