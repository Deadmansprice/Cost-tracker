##### - UserManagement.py:
from hashlib import sha256
import json
from pathlib import Path
import Common
from PySide6.QtWidgets import QInputDialog, QLineEdit
import CostCell
import os

class UserManagement:
    failed_login_attempts = {}
    def __init__(self):
        self.login_data = self.load_login_data()

    #This function hashes password using SHA-256 and returns hashed value. 
    def hash_password(self, password):
        return sha256(password.encode()).hexdigest()
    
    #default directory is at the main.py.
    def create_user_via_dialogue(self, main_window):
        username, ok_username = QInputDialog.getText(main_window, "Username", "Enter your username:")
        if ok_username:
            password, ok_password = QInputDialog.getText(main_window, "Password", "Enter your password:", QLineEdit.Password)
            if ok_password:
                Common.create_user_data(username, password)
                self.CostCell_window_open(username)
                
    def create_user_and_data(self, username, password):
        hashed_password = sha256(password.encode()).hexdigest()
        self.login_data[username] = hashed_password
        self.save_login_data

    def close(self):
        print("closing UserManagement")

    def CostCell_window_open(self, username):
        self.close()
        self.new_window = CostCell.CostCell(username)
        self.new_window.show()

    def my_callback(username):
        new_window = CostCell(username)
        new_window.show()

    
    #Loads the login data from JSON file, and retursn empty dictionary if file does not exist or cannot be read.
    def load_login_data(self):
        json_file_path = os.path.join(Common.get_current_directory(), "login_data.json")
        if Path(json_file_path).exists():
            with open(json_file_path, "r") as file:
                return json.load(file)
        return {}

    #Login data is saved to a JSON file via this function
# Correct the print statement
    def save_login_data(self):
        json_file_path = os.path.join(Common.get_current_directory(), "login_data.json")
        os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
        with open(json_file_path, "w") as file:
                json.dump(self.login_data, file)
  
    def create_user(self, username, password):
        self.login_data[username] = self.hash_password(password)    
        self.save_login_data()

    def check_login_data(self):
        return UserManagement.load_login_data()
   
    def validate_password(self, username,password):
        correct_password_hash = self.login_data[username]
        entered_password_hash = self.hash_password(password)
        if correct_password_hash == entered_password_hash:
            print("Access granted")
            return True
        else: 
            print("Incorrect password")
            UserManagement.increment_failed_login(username)
            if UserManagement.check_failed_login(username) >=3:
                print("You have incorrectly entered your password three times. The username and relevant cost tracking data has been purged for security purposes.")
            return False    

    @classmethod
    def increment_failed_login(cls, username):
        cls.failed_login_attempts[username] = cls.failed_login_attempts.get(username, 0) + 1

    @classmethod
    def check_failed_login(cls, username):
        return cls.failed_login_attempts.get(username, 0)