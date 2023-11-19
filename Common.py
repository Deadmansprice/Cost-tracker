from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QInputDialog
import CostCell
import UserManagement
import DataManager
from pathlib import Path

#Variables to be used by all the files to keep it dynamic. Necessary when wrking with multiple files.
JSON_FILENAME = "login_data.json"
FOLDER_PATH_FILENAME = "folder_path.json"
CSV_FILENAME = "cost_tracking_app.csv"

#Creation of user data upon first launch
def create_user_data(username, password, default_directory):
    if default_directory is None:
        default_directory = FOLDER_PATH_FILENAME

    tracking_data_folder = Path(default_directory, "Cost Tracking Data")
    tracking_data_folder.mkdir(parents=True, exist_ok=True)
        
    user_management = DataManager.Returner.create_user_management()
    json_file_path, csv_file_path =  get_file_paths(default_directory, username)
    hashed_password = user_management.hash_password(password)
    user_management.login_data[username] = hashed_password
    
    user_management.save_login_data(user_management.login_data)
    data_manager = DataManager.DataManager(username)
    data_manager.create_empty_csv()
    

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