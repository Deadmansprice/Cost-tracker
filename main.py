from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog #inital set up of the application
from pathlib import Path
import DataManager
from Common import user_list_window
from Common import JSON_FILENAME, CSV_FILENAME
import pandas as pd
import time, sys, os
import UserManagement

#Main window at the start for local user login
class MainWindow(QMainWindow): 
    def __init__(self):
        super().__init__()
        self.new_window = None
        self.setWindowTitle("Cost Tracker")
        self.user_management = DataManager.Returner.create_user_management() #Refer to DataManger.py. It leads to #UserManagement for account creation on start.
        self.UserData = UserManagement.UserManagement() #Boots up UserManagement Class for logins.
        print("Loaded login data:", self.user_management.login_data)
        self.default_directory = None
     
        self.layout = QVBoxLayout()

        button_start = QPushButton("Existing User/s" if Path(CSV_FILENAME).exists() else "Create User")
        button_start.clicked.connect(self.open_CostCell)
        self.layout.addWidget(button_start)

        if Path(CSV_FILENAME).exists():
            button_create_another_user = QPushButton("Create another user?") 
            button_create_another_user.clicked.connect(lambda: self.UserData.create_user_and_data(self.default_directory, self.new_window))
            self.layout.addWidget(button_create_another_user)
    
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    #Giving user to set file path on where they are saving the folder where their data should be saved in.
    def set_file_path(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.default_directory = folder
    
    #refer to CostCell.Py for modification of that file.
    def open_CostCell(self):
        if Path(JSON_FILENAME).exists():
            self.user_list_window = user_list_window()
            self.user_list_window.show()
        else:
            self.UserData.create_user_and_data(self.default_directory, self)

    def openNewWindow(self):
        self.close()
        self.new_window = user_list_window()
        self.new_window.show()

    def reload_data(self):
        #Reloads relevant data from CSV file
        self.df = pd.read_csv(DataManager.CSV_FILE)

        if hasattr(self, 'new_window'):
            self.new_window.update_table(self.df)              

    #Allows the user to choose location on where to save the data.    
    def saveFileDialogue(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        csv_exists = Path(DataManager.CSV_FILE).exists()
        json_exists = Path("login_data.json").exists()

        dialog = QFileDialog(self, "Save File As", "", "CSV Files (*.csv); All Files (*)")
        dialog.setOptions(options)

        if not (csv_exists and json_exists):
            if self.default_directory is None:
                self.default_directory = f"default_dir_{int(time.time())}"
                Path(self.default_directory).mkdir(parents = True, exist_ok=True)
            dialog.setDirectory(self.default_directory) #allows user to set a default system as to where csv and json files will be placed in.
        elif csv_exists and json_exists:
            dialog.setDirectory(os.path.expanduser("~"))

        if dialog.exec() == QFileDialog.Accepted:
            fileName = dialog.selectedFiles()[0]
            print(fileName)
                 
#variables
app = QApplication(sys.argv)
window = MainWindow()
window.show() #Shows the window. 
app.exec() #Begins the event loop