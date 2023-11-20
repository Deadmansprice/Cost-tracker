from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
from PySide6.QtCore import Qt, QTimer #For the app settings
from datetime import datetime
from CSVManagement import CSVManagement
import calendar
import pandas as pd
import platform
import os, Common

# For the UI of CostCell. Handles the appearance and buttonns.
class CostCellUI(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.data_2d_list = []

        if not os.path.exists(Common.default_directory):
            os.makedirs(Common.default_directory)

        _, csv_file_path = Common.get_file_paths(Common.default_directory, self.username)


        self.csv_manager = CSVManagement(self.username, self.data_2d_list)
        self.data_2d_list = self.load_csv_data(csv_file_path)
        self.layout = QVBoxLayout(self)
        self.headerlabels = ['Food', 'Fuel', 'Bills', 'Investments', 'Miscellaneous']
        _, num_days = calendar.monthrange(datetime.now().year, datetime.now().month)

        
        self.setup_user_label()
        self.setup_table()
        self.setup_buttons()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_headers)
        self.timer.start(30000) #Save every 30 seconds
        self.update_headers()
        self.setLayout(self.layout)

    #Header update. checks the local system for date/time and sees if it's current month, if the month has passed then it will create a new file for that newly-current month.
    def update_headers(self):
        self.csv_manager.new_month_check()
        current_date = datetime.now()
        formatted_date = current_date.strftime("%-d %B %Y") if platform.system() != 'Windows' else current_date.strftime("%#d %B %Y")
        
        #Ensure table widget has been initialised before trying to access its headers
        if hasattr(self, 'table'):
            current_headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            if formatted_date not in current_headers:
                self.add_new_day_column()

    def load_csv_data(self, csv_file_path):
        #verifies existence of CSV file
        if not os.path.exists(csv_file_path):
            # Handle the absence of the file, for example, by creating an empty DataFrame
            empty_df = pd.DataFrame()
            # Optionally save the empty DataFrame to create the file
            empty_df.to_csv(csv_file_path, index=False)
            return empty_df
        else:
            #If the file exists, proceed to load it as before.
            cost_frame = pd.read_csv(csv_file_path)
            return cost_frame

    def setup_user_label(self):
        if self.username is None:
            self.username_label_text = "Welcome, New_User"

        else: 
            self.username_label_text = (f"Welcome back, {self.username}")
        self.user_label = QLabel(self.username_label_text)
        self.layout.addWidget(self.user_label)
    
    #Inital excel
    def setup_table(self):
        self.table = QTableWidget()
        #dynamic rows and columns below
        self.table.setRowCount(len(self.headerlabels))
        self.table.setColumnCount(1) #initially only 1 column for today
        today = datetime.now().strftime(("%d %B %Y"))
        self.table.setHorizontalHeaderLabels([today])
        for row in range(len(self.headerlabels)):
            for col in range(self.table.columnCount()):
                self.table.setItem(row, col, QTableWidgetItem(""))
        self.populate_table_with_csv_data()
        self.layout.addWidget(self.table)

    def populate_table_with_csv_data(self):
        for row_index, row_data in enumerate(self.data_2d_list):
            for col_index, cell_data in enumerate(row_data):
                self.table.setItem(row_index, col_index, QTableWidgetItem(cell_data))

    def setup_buttons(self):
        self.previous_months_button = QPushButton("Previous Months")
        self.add_row_button = QPushButton('+')
        self.layout.addWidget(self.previous_months_button)
        self.layout.addWidget(self.add_row_button)

    def add_new_day_column(self):
        today = datetime.now().strftime("%d %B %Y")
        new_column_index = self.table.columnCount()
        self.table.insertColumn(new_column_index)
        self.table.setHorizontalHeaderItem(new_column_index, QTableWidgetItem(today))
        for row in range(self.table.rowCount()):
            self.table.setItem(row, new_column_index, QTableWidgetItem(""))
        self.csv_manager.save_to_csv()

## Back end event handling depending on what the user is selecting within the UI
class CostCellEventHandler:
    def __init__(self, ui):
        self.ui = ui
        self.connect_events()
    
        self.ui.table.verticalHeader().sectionPressed.connect(self.header_clicked)
        self.ui.table.cellClicked.connect(self.cell_was_clicked)

        #timer for saving
        self.auto_save_timer = QTimer(self.ui)
        self.auto_save_timer.timeout.connect(self.auto_save_method)
        self.auto_save_timer.timeout.connect(self.ui.csv_manager.save_to_csv)
        self.auto_save_timer.start(5000) #Timer in milliseconds. 5000 ms for 5 seconds.

    def connect_events(self):
        self.ui.previous_months_button.clicked.connect(self.handle_previous_months)
        self.ui.add_row_button.clicked.connect(self.add_row)
        self.ui.table.cellChanged.connect(self.cell_changed)

    def handle_previous_months(self):
        pass #Not yet implemented.

    def add_row(self):
        row_position = self.ui.table.rowCount()
        self.ui.table.insertRow(row_position)
        for col in range(self.ui.table.columnCount()):
            item = QTableWidgetItem()
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.ui.table.setItem(row_position, col, item)

    def cell_changed(self, row, column):
        if row >= len(self.ui.data_2d_list):
            print("Row index out of range")
            return
        if column >= len(self.ui.data_2d_list[row]):
            print("Column index out of range")
            return
        
        new_value = self.ui.table.item(row,column).text()
        self.ui.data_2d_list[row][column] = new_value
        self.ui.csv_manager.save_to_csv()

    def header_clicked(self, index):
        self.selected_row_index = index

    def cell_was_clicked(self,row, column):
        print(f"Cell ({row}, {column}) was clicked")
        item = self.ui.table.item(row, column)
        if item:
            print("item flags", item.flags())

    def auto_save_method(self):
        self.ui.csv_manager.save_to_csv()


#Main window suppored by UI settings and Event handler. It's just for the tables within.
class CostCell(QMainWindow): 
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("Cost Cell")
        self.username = username
        self.ui = CostCellUI(self.username) #Refer to above class with same name.
        self.event_handler = CostCellEventHandler(self.ui) #refer to above class with same name. Note, we are using .ui for the below tables.
        self.setCentralWidget(self.ui)

       
        self.selected_row_index = None

        
        for row in range(self.ui.table.rowCount()):
            for col in range(self.ui.table.columnCount()):
                item = QTableWidgetItem()
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                print("Item flags:", item.flags())
                self.ui.table.setItem(row, col, item)

        self.ui.table.setVerticalHeaderLabels(self.ui.headerlabels)
        self.ui.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.ui.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.ui.table.setShowGrid(True)
        self.ui.table.setGridStyle(Qt.SolidLine)
    
    def reset_table_monthly(self):
        self.ui.table.clear()
        self.initialize_table_headers()
    
    def table_data_refresh(self):
        self.ui.table.clear()
        self.ui.table.setRowCount(len(self.data_2d_list))
        for row_index, row in enumerate(self.data_2d_list):
            for col_index, cell in enumerate(row):
                item = QTableWidgetItem(cell)
                self.ui.table.setItem(row_index, col_index, item)
        self.ui.table.resizeColumnsToContents()

    def update_table_ui(self):
        self.ui.table.clearContents()
        self.ui.table.setRowCount(len(self.data_2d_list))
        self.ui.table.setColumnCount(len(self.data_2d_list[0]) if self.data_2d_list else 0)

        for row_index, row in enumerate(self.data_2d_list):
            for col_index, item in enumerate(row):
                self.ui.table.setItem(row_index, col_index, QTableWidgetItem(str(item)))

    #Checks to see if the column is either for today, or if day has passed then update to today.
    def ensure_today_column(self):
        today = datetime.now().strftime("%d %B %Y")
        if not hasattr(self, 'ui'):
            return
        
        current_headers = [self.ui.table.horizontalHeaderItem(i).text() for i in range(self.ui.table.columnCount())]
        if today not in current_headers:     
            col_index = self.ui.table.columnCount()
            self.ui.table.insertColumn(col_index)
            self.ui.table.setHorizontalHeaderItem(col_index, QTableWidgetItem(today))
            for row in self.data_2d_list:
                row.append("")
            self.ui.table.resizeColumnsToContents()

    def add_column_addition(self):
        today = datetime.now().strftime("%d %B %Y")
        current_headers = [self.ui.table.horizontalHeaderItem(i).text() for i in range(self.ui.table.columnCount())]

        if today not in current_headers: #New column for today
            self.ui.table.insertColumn(self.ui.table.columnCount())
            self.ui.table.setHorizontalHeaderItem(self.ui.table.columnCount() - 1, QTableWidgetItem(today))

            #new column in data structure
            for row in self.data_2d_list:
                row.append("")

            self.ui.table.resizeColumnsToContents()

                   
    def input_replace(self, cost_button):
        cost = cost_button.text()
        input_field = QLineEdit(cost)
        input_field.editingFinished.connect(lambda: self.add_cost_button(input_field))
        self.layout.replaceWidget(cost_button, input_field)

    def update_table(self, new_cf):
        if not isinstance(new_cf, pd.DataFrame):
            return #Handles the error appropriately
        
        self.ui.table.setRowCount(0) #table clearance
        for index, row in new_cf.iterrows():
            row_position = self.ui.table.rowCount()
            self.ui.table.insertRow(row_position)
            for col_num, value in enumerate(row):
                item = QTableWidgetItem(str(value) if value else "")
                self.ui.table.setItem(row_position, col_num, item)
        self.ui.table.resizeColumnsToContents()

    def closeEvent(self, event):
        self.ui.csv_manager.save_to_csv()
        event.accept()
