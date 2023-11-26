##### - main.py: 
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,QMessageBox, QFileDialog, QInputDialog, QLineEdit
from pathlib import Path
import Common
import pandas as pd
import sys, os
import UserManagement
import CSVManagement
import CostCell

#Main window at the start for local user login
class MainWindow(QMainWindow): 
    def __init__(self):
        super().__init__()
        self.new_window = None
        self.setWindowTitle("Cost Tracker")
        self.user_management = UserManagement.UserManagement() #Refer to DataManger.py. It leads to #UserManagement for account creation on start.
        self.UserData = UserManagement.UserManagement() #Boots up UserManagement Class for logins.
        self.username = None
        self.data_2d_list = []
        print("Loaded login data:", self.user_management.login_data)
     
        self.layout = QVBoxLayout()

        button_start = QPushButton("Existing User/s" if Path(Common.CSV_FILENAME).exists() else "Create User")
        button_start.clicked.connect(self.open_CostCell)
        print(f"Your files are located within {Common.default_directory}")
        self.layout.addWidget(button_start)

        if Path(Common.CSV_FILENAME).exists():
            button_create_another_user = QPushButton("Create another user?") 
            button_create_another_user.clicked.connect(lambda: self.UserData.create_user_and_data(Common.default_directory, self.new_window))
            self.layout.addWidget(button_create_another_user)
    
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        csv_exists = Path(Common.CSV_FILENAME).exists()
        json_exists = Path(Common.JSON_FILENAME).exists()

        if not (csv_exists and json_exists):
            self.set_file_path_dialogue()

    def set_file_path_dialogue(self):
        choice = QMessageBox.question(self, 'Setup Requred', "CSV or JSON file not found. Would you like to set a file path for saving data?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if choice == QMessageBox.Yes:
            self.choose_new_directory()
        else:
            self.UserData.create_user_and_data(Common.default_directory, self)

    def choose_new_directory(self):
        options = QFileDialog.Options()
        new_directory = QFileDialog.getExistingDirectory(self, "Select Directory", Common.default_directory, options=options)
        if new_directory:
            Common.update_default_directory(new_directory)
        else:
            print("Directory selection was canceled.")

    #Giving user to set file path on where they are saving the folder where their data should be saved in.
    def set_file_path(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            Common.default_directory = folder
    
    #refer to CostCell.Py for modification of that file.
    def open_CostCell(self):  
        if Path(Common.JSON_FILENAME).exists():
            self.user_list_window = Common.user_list_window()
            self.user_list_window.show()
        else:
            self.UserData.create_user_via_dialogue(self)

    def openNewWindow(self):
        self.close()
        self.new_window = Common.user_list_window()
        self.new_window.show()

    def reload_data(self):
        #Reloads relevant data from CSV file
        self.csv_manager = CSVManagement.CSVManagement(self.username, self.data_2d_list)
        self.data_2d_list = self.csv_manager.csv_data_load(Common.CSV_FILENAME)

    def openCostCell(self):
        self.cost_cell_instance = CostCell.CostCell(self.username)
        self.cost_cell_instance.show()

    def setUserDetails(self, username, data_2d_list):
        self.username = username
        self.data_2d_list = data_2d_list

        if hasattr(self, 'cost_cell_instance'):
            self.cost_cell_instance.update_table(self.data_2d_list)

    #Allows the user to choose location on where to save the data.    
    def saveFileDialogue(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ShowDirsOnly

        dialog = QFileDialog(self, "Select Folder", "")
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOptions(options)

        if dialog.exec() == QFileDialog.Accepted:
            selected_directory = os.path.dirname(dialog.selectedFiles()[0])
            Common.default_directory = selected_directory
            print("New directory set:", Common.default_directory)
            print("Directory selected:", Common.default_directory)
            if self.username is not None and self.data_2d_list is not None:
                csv_manager = CSVManagement.CSVManagement(self.username, self.data_2d_list)
                csv_manager.save_to_csv(save_directory=selected_directory, headerlabels=self.headerlabels)    
            else:
                # Handle the case where username or data_2d_list is not set
                QMessageBox.warning(self, "Error", "User details are not set.")
#variables
app = QApplication(sys.argv)
window = MainWindow()
window.show() #Shows the window. 
app.exec() #Begins the event loop