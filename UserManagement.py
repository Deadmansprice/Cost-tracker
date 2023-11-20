from hashlib import sha256
import json
from pathlib import Path
import Common
from PySide6.QtWidgets import QInputDialog
import CostCell

class UserManagement:
    failed_login_attempts = {}
    def __init__(self):
        self.login_data = self.load_login_data()

    #This function hashes password using SHA-256 and returns hashed value. 
    def hash_password(self, password):
        return sha256(password.encode()).hexdigest()
    

    #default directory is at the main.py.
    def create_user_and_data(self, default_directory, main_window):
        username, ok = QInputDialog.getText(main_window, "Username", "Enter your username:")
        if ok:
            password, ok = QInputDialog.getText(main_window, "Password", "Enter your password:")
            if ok:
                Common.create_user_data(username, password, default_directory)
                self.CostCell_window_open(username)

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
        try:
            if Path(Common.JSON_FILENAME).exists():
                with open(Common.JSON_FILENAME, "r")as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"An error occured while loading login data: {e}")
            return {}
    
    #Login data is saved to a JSON file via this function
# Correct the print statement
    def save_login_data(self, data):
        try:
            with open(Common.JSON_FILENAME, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"An error occurred while saving login data: {e}")

  
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
    

    #For Folder saving. See Common.py for more details. 
    @classmethod
    def save_folder_path(cls, folder_path):
        with open(Common.FOLDER_PATH_FILENAME, "w") as f:
            json.dump({"folder_path": folder_path}, f)

    @classmethod
    def load_folder_path(cls):
        if Path(cls.Common.FOLDER_PATH_FILENAME).exists():
            with open(Common.FOLDER_PATH_FILENAME, "r") as f:
                data = json.load(f)
            return data.get("folder_path", "")
        return ""