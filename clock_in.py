import sys
import os
import csv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QComboBox,
                             QLineEdit, QDialog, QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QMessageBox, QDialogButtonBox, QDateEdit, QTextEdit)
from PyQt5.QtCore import QDateTime, QDate, QTimer, Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
import math
import pyqtgraph as pg
from datetime import datetime, time
from collections import defaultdict

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(600, 200, 300, 150)
        self.setStyleSheet("background-color: white;")
        self.setFixedSize(300, 200)
        self.setWindowIcon(QIcon("dsalogo-297x300.png"))
        layout = QVBoxLayout()

        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.setStyleSheet("background-color: white; color: darkgreen; font-weight: bold;")
        self.setFont(font)

        self.username_label = QLabel("Username:", self)
        layout.addWidget(self.username_label)

        self.username_input = QLineEdit(self)
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:", self)
        layout.addWidget(self.password_label)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login", self)
        self.login_button.setFont(font)
        self.login_button.setStyleSheet("background-color: darkgreen; color: white;")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

        self.valid_username = "admin"
        self.valid_password = "dcsadmin"

    def login(self):
        entered_username = self.username_input.text()
        entered_password = self.password_input.text()

        if entered_username == self.valid_username and entered_password == self.valid_password:
            print("Login successful!")
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Invalid username or password. Please try again.")
            self.username_input.clear()
            self.password_input.clear()
            self.username_input.setFocus()
class AddStaffDialog(QDialog):
    def __init__(self, table_widget):
        super().__init__()
        self.setWindowTitle("Add New Staff")
        self.setWindowIcon(QIcon("dsalogo-297x300.png"))
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()

        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.setStyleSheet("background-color: white; color: darkgreen; font-weight: bold;")
        self.setFont(font)

        self.staff_id_label = QLabel("Staff ID:")
        self.staff_id_input = QLineEdit()
        layout.addWidget(self.staff_id_label)
        layout.addWidget(self.staff_id_input)

        self.directorate_label = QLabel("Directorate:")
        self.directorate_input = QLineEdit()
        layout.addWidget(self.directorate_label)
        layout.addWidget(self.directorate_input)

        self.staff_type_label = QLabel("Staff Type:")
        self.staff_type_input = QLineEdit()
        layout.addWidget(self.staff_type_label)
        layout.addWidget(self.staff_type_input)

        self.full_name_label = QLabel("Full Name:")
        self.full_name_input = QLineEdit()
        layout.addWidget(self.full_name_label)
        layout.addWidget(self.full_name_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_save)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)
        self.table_widget = table_widget

    def validate_and_save(self):
        staff_id = self.staff_id_input.text().strip()
        directorate = self.directorate_input.text().strip()
        staff_type = self.staff_type_input.text().strip()
        full_name = self.full_name_input.text().strip()

        if not staff_id or not directorate or not staff_type or not full_name:
            QMessageBox.warning(self, "Warning", "All fields must be filled.")
            return

        self.save_data()

    def save_data(self):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        self.table_widget.setItem(row_position, 0, QTableWidgetItem(self.staff_id_input.text()))
        self.table_widget.setItem(row_position, 1, QTableWidgetItem(self.directorate_input.text()))
        self.table_widget.setItem(row_position, 2, QTableWidgetItem(self.staff_type_input.text()))
        self.table_widget.setItem(row_position, 3, QTableWidgetItem(self.full_name_input.text()))

        with open("staff_data.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([self.staff_id_input.text(), self.directorate_input.text(), self.staff_type_input.text(), self.full_name_input.text()])

        QMessageBox.information(self, "Success", "New staff added successfully.")
        self.accept()

class RemoveStaffDialog(QDialog):
    def __init__(self, table_widget):
        super().__init__()
        self.setWindowTitle("Remove Staff")
        self.setWindowIcon(QIcon("dsalogo-297x300.png"))
        self.setFixedSize(400, 100)
        layout = QVBoxLayout()

        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.setStyleSheet("background-color: white; color: darkgreen; font-weight: bold;")
        self.setFont(font)

        self.staff_id_label = QLabel("Staff ID:")
        self.staff_id_input = QLineEdit()
        layout.addWidget(self.staff_id_label)
        layout.addWidget(self.staff_id_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self.remove_data)
        button_box.addButton(remove_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)
        self.table_widget = table_widget

    def remove_data(self):
        staff_id = self.staff_id_input.text().strip()
        
        if not staff_id:
            QMessageBox.warning(self, "Warning", "Staff ID must be provided.")
            return

        if not self.check_existing_id(staff_id):
            QMessageBox.warning(self, "Warning", "Staff ID does not exist.")
            return

        self.remove_staff()

    def check_existing_id(self, staff_id):
        rows = self.table_widget.rowCount()
        for row in range(rows):
            if self.table_widget.item(row, 0).text() == staff_id:
                return True
        return False

    def remove_staff(self):
        rows = self.table_widget.rowCount()
        for row in range(rows):
            if self.table_widget.item(row, 0).text() == self.staff_id_input.text():
                self.table_widget.removeRow(row)
                break

        with open("staff_data.csv", "r") as file:
            lines = file.readlines()

        with open("staff_data.csv", "w") as file:
            for line in lines:
                if self.staff_id_input.text() not in line:
                    file.write(line)

        QMessageBox.information(self, "Success", "Staff removed successfully.")
        self.accept()

class AnalyticsDialog(QDialog):
    def __init__(self, clock_in_data, present_percentage, late_percentage, absent_percentage):
        super().__init__()
        
        self.clock_in_data = clock_in_data
        self.present_percentage = present_percentage
        self.late_percentage = late_percentage
        self.absent_percentage = absent_percentage
        
        print("Present percentage before creating dialog:", self.present_percentage)
        print("Late percentage before creating dialog:", self.late_percentage)
        print("Absent percentage before creating dialog:", self.absent_percentage)

        self.setWindowTitle("Generate Analytics")
        self.setWindowIcon(QIcon("dsalogo-297x300.png"))
        self.setGeometry(100, 100, 800, 600)

        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        
        self.setStyleSheet("background-color: white; color: darkgreen; font-weight: bold;")
        self.setFont(font)

        self.layout = QVBoxLayout()

        self.canvas = FigureCanvas(Figure(figsize=(5, 5), dpi=100))
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)

    def draw_pie(self):
        print("Data for pie chart:", [self.present_percentage, self.late_percentage, self.absent_percentage])

        sizes = [self.present_percentage, self.late_percentage, self.absent_percentage]
        labels = ['Present', 'Late', 'Absent']

        fig, ax = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, labeldistance=1.2)
        ax.axis('equal')

        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontsize(12)

        ax.xaxis.labelpad = 20

        for label, autotext in zip(labels, autotexts):
            x, y = autotext.get_position()
            if label == 'Present':
                autotext.set_position((x, y + 0.1))
            elif label == 'Absent':
                autotext.set_position((x, y - 0.1))

        self.canvas.figure = fig
        self.canvas.draw()

class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search")
        self.setGeometry(600, 300, 400, 200)
        self.setStyleSheet("background-color: white;")
        self.setFixedSize(400, 200)
        self.setWindowIcon(QIcon("dsalogo-297x300.png"))

        layout = QVBoxLayout()

        self.search_staff_id_label = QLabel("Search Staff ID:", self)
        layout.addWidget(self.search_staff_id_label)

        self.search_id_input = QLineEdit(self)
        layout.addWidget(self.search_id_input)

        self.start_date_label = QLabel("Start Date:", self)
        layout.addWidget(self.start_date_label)

        self.start_date_edit = QDateEdit(self)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.start_date_edit)

        self.end_date_label = QLabel("End Date:", self)
        layout.addWidget(self.end_date_label)

        self.end_date_edit = QDateEdit(self)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.end_date_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

class SearchResultsDialog(QDialog):
    def __init__(self, results, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Results")
        self.setGeometry(600, 300, 600, 400)
        self.setStyleSheet("background-color: white;")
        self.setFixedSize(600, 400)
        self.setWindowIcon(QIcon("dsalogo-297x300.png"))

        layout = QVBoxLayout()

        self.table_widget = QTableWidget(self)
        self.table_widget.setRowCount(len(results))
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["Date", "Staff Name", "Directorate", "Staff Type", "Status", "Time"])

        for row_index, result in enumerate(results):
            self.table_widget.setItem(row_index, 0, QTableWidgetItem(result["Date"]))
            self.table_widget.setItem(row_index, 1, QTableWidgetItem(result["Staff Name"]))
            self.table_widget.setItem(row_index, 2, QTableWidgetItem(result["Directorate"]))
            self.table_widget.setItem(row_index, 3, QTableWidgetItem(result["Staff Type"]))
            self.table_widget.setItem(row_index, 4, QTableWidgetItem(result["Status"]))
            self.table_widget.setItem(row_index, 5, QTableWidgetItem(result["Time"]))

        self.table_widget.resizeColumnsToContents()
        layout.addWidget(self.table_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)

class ClockInRegister(QMainWindow):
    def __init__(self):
        super().__init__()
        self.login_dialog = LoginDialog()
        if not self.login_dialog.exec_():
            sys.exit(1)
        
        self.setWindowTitle("Clock-in Register")
        self.setGeometry(200, 100, 900, 600)
        self.setStyleSheet("background-color: white;")
        self.setFixedSize(800, 600)

        input_width = 200
        input_height = 30
        input_margin = 20
        x_offset = 150

        self.image_label = QLabel(self)
        self.image_label.setGeometry(280, 50, 200, 200)
        pixmap = QPixmap("dsalogo-297x300.png")
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)

        self.set_window_icon("dsalogo-297x300.png")

        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.setStyleSheet("background-color: white; color: darkgreen; font-weight: bold;")
        self.setFont(font)

        self.staff_id_label = QLabel("Staff ID:", self)
        self.staff_id_label.setGeometry(x_offset, 300, 100, input_height)
        self.staff_id_label.setStyleSheet("color: darkgreen; font-weight: bold;")

        self.id_input = QLineEdit(self)
        self.id_input.setGeometry(x_offset + 100 + input_margin, 300, input_width, input_height)
        self.id_input.setStyleSheet("background-color: white; border: 1px solid darkgreen;")
        self.id_input.textChanged.connect(self.populate_staff_details)

        self.staff_name_label = QLabel("Staff Name:", self)
        self.staff_name_label.setGeometry(x_offset, 350, 100, input_height)
        self.staff_name_label.setStyleSheet("color: darkgreen; font-weight: bold;")

        self.staff_name_display = QLabel(self)
        self.staff_name_display.setGeometry(x_offset + 100 + input_margin, 350, input_width, input_height)
        self.staff_name_display.setStyleSheet("background-color: white; border: 1px solid darkgreen; padding: 2px;")

        self.directorate_label = QLabel("Directorate:", self)
        self.directorate_label.setGeometry(x_offset, 400, 100, input_height)
        self.directorate_label.setStyleSheet("color: darkgreen; font-weight: bold;")

        self.directorate_display = QLabel(self)
        self.directorate_display.setGeometry(x_offset + 100 + input_margin, 400, input_width, input_height)
        self.directorate_display.setStyleSheet("background-color: white; border: 1px solid darkgreen; padding: 2px;")

        self.staff_type_label = QLabel("Staff Type:", self)
        self.staff_type_label.setGeometry(x_offset, 450, 100, input_height)
        self.staff_type_label.setStyleSheet("color: darkgreen; font-weight: bold;")

        self.staff_type_display = QLabel(self)
        self.staff_type_display.setGeometry(x_offset + 100 + input_margin, 450, input_width, input_height)
        self.staff_type_display.setStyleSheet("background-color: white; border: 1px solid darkgreen; padding: 2px;")

        self.clock_in_button = QPushButton("Clock In", self)
        self.clock_in_button.move(150, 500)
        self.clock_in_button.setFixedWidth(120)
        self.clock_in_button.clicked.connect(self.clock_in)
        self.clock_in_button.setStyleSheet("background-color: darkgreen; color: white; border: none; padding: 5px 10px; font-weight: bold;")

        self.view_db_button = QPushButton("Today's Data", self)
        self.view_db_button.move(280, 500)
        self.view_db_button.setFixedWidth(120)
        self.view_db_button.clicked.connect(self.view_database)
        self.view_db_button.setStyleSheet("background-color: darkgreen; color: white; border: none; padding: 5px 10px; font-weight: bold;")
        
        self.view_staff_data_button = QPushButton("View Staff Data", self)
        self.view_staff_data_button.move(410, 500)
        self.view_staff_data_button.setFixedWidth(120)
        self.view_staff_data_button.clicked.connect(self.view_staff_data)
        self.view_staff_data_button.setStyleSheet("background-color: darkgreen; color: white; border: none; padding: 5px 10px; font-weight: bold;")

        self.generate_analytics_button = QPushButton("Generate Analytics", self)
        self.generate_analytics_button.move(540, 500)
        self.generate_analytics_button.setFixedWidth(130)
        self.generate_analytics_button.clicked.connect(self.generate_analytics)
        self.generate_analytics_button.setStyleSheet("background-color: darkgreen; color: white; border: none; padding: 5px 10px; font-weight: bold;")
        
        self.search_button = QPushButton("Search", self)
        self.search_button.setGeometry(680, 500, 120, input_height)
        self.search_button.setStyleSheet("background-color: darkgreen; color: white; border: none; padding: 5px 10px; font-weight: bold;")
        self.search_button.clicked.connect(self.open_search_dialog)
                
        self.clock_in_button.clicked.connect(self.highlight_button)
        self.view_db_button.clicked.connect(self.highlight_button)
        self.view_staff_data_button.clicked.connect(self.highlight_button)
        self.generate_analytics_button.clicked.connect(self.highlight_button)
        
        self.clock_in_message_label = QLabel("", self)
        self.clock_in_message_label.setGeometry(x_offset, 550, 300, 20)
        self.clock_in_message_label.setStyleSheet("color: red;")

        self.plot_widget = pg.PlotWidget(title="Monthly Statistics")
        self.plot_widget.move(50, 300)
        self.plot_widget.resize(600, 300)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_time)
        self.timer.start(60000)
        
        self.highlight_timer = QTimer(self)
        self.highlight_timer.setSingleShot(True)
        self.highlight_timer.timeout.connect(self.reset_button_style)
        self.highlight_timer.start(300)

        self.clock_in_data_filename = f"clock_in_data_{datetime.now().strftime('%d-%m-%Y')}.csv"
        self.load_clock_in_data(self.clock_in_data_filename)

        self.present_percentage = 0
        self.late_percentage = 0
        self.absent_percentage = 0

    def set_window_icon(self, icon_path):
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)

    def highlight_button(self):
        sender = self.sender()
        sender.setStyleSheet("background-color: #228B22; color: white; border: none; padding: 5px 10px; font-weight: bold;")
        self.highlight_timer.start(300)

    def reset_button_style(self):
        self.clock_in_button.setStyleSheet("background-color: darkgreen; color: white; border: none; padding: 5px 10px; font-weight: bold;")
        self.view_db_button.setStyleSheet("background-color: darkgreen; color: white; border: none; padding: 5px 10px; font-weight: bold;")
        self.view_staff_data_button.setStyleSheet("background-color: darkgreen; color: white; border: none; padding: 5px 10px; font-weight: bold;")
        self.generate_analytics_button.setStyleSheet("background-color: darkgreen; color: white; border: none; padding: 5px 10px; font-weight: bold;")
    
    def view_staff_data(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Staff Data")
        dialog.setFixedSize(630, 300)
        layout = QVBoxLayout()

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Staff ID", "Directorate", "Staff Type", "Full Name"])

        try:
            with open("staff_data.csv", "r", newline="") as file:
                reader = csv.reader(file)
                next(reader)
                data = list(reader)
                table.setRowCount(len(data))
                for i, row in enumerate(data):
                    for j, value in enumerate(row):
                        item = QTableWidgetItem(value)
                        table.setItem(i, j, item)
        except FileNotFoundError:
            print("Error: staff_data.csv not found.")

        layout.addWidget(table)
        dialog.setLayout(layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.save_staff_data(table))
        button_box.rejected.connect(dialog.reject)

        add_new_button = QPushButton("Add New Staff")
        add_new_button.clicked.connect(lambda: self.add_new_staff(table))
        add_new_button.setFixedWidth(120)

        remove_button = QPushButton("Remove Staff")
        remove_button.clicked.connect(lambda: self.remove_staff(table))
        remove_button.setFixedWidth(120)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_new_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(button_box)
    
        layout.addLayout(button_layout)
    
        dialog.setLayout(layout)
        dialog.rejected.connect(lambda: self.load_staff_names_from_csv("staff_data.csv"))
        dialog.exec_()

    def add_new_staff(self, table):
        add_dialog = AddStaffDialog(table)
        if add_dialog.exec_() == QDialog.Accepted:
            self.load_staff_names_from_csv("staff_data.csv")

    def remove_staff(self, table):
        remove_dialog = RemoveStaffDialog(table)
        if remove_dialog.exec_() == QDialog.Accepted:
            self.load_staff_names_from_csv("staff_data.csv")

    def save_staff_data(self, table):
        try:
            with open("staff_data.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["staff_id", "directorate", "staff_type", "full_name"])
                for row in range(table.rowCount()):
                    row_data = [table.item(row, col).text() for col in range(table.columnCount())]
                    writer.writerow(row_data)
            print("Staff data saved successfully.")
            QMessageBox.information(self, "Success", "Staff data saved successfully.")
        except Exception as e:
            print(f"Error saving staff data: {e}")
            QMessageBox.warning(self, "Error", f"Error saving staff data: {e}")

    def load_staff_names_from_csv(self, filename):
        try:
            with open(filename, "r") as file:
                reader = csv.DictReader(file)
                staff_names = [row["full_name"] for row in reader]
                self.staff_name_combo.clear()
                self.staff_name_combo.addItems(staff_names)
                print("Staff names loaded successfully:", staff_names)
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
        except Exception as e:
            print(f"Error loading staff names: {e}")

    def populate_staff_details(self):
        staff_id = self.id_input.text().strip()
        print("Staff ID:", staff_id)
        if staff_id:
            try:
                with open("staff_data.csv", "r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row["staff_id"] == staff_id:
                            self.staff_name_display.setText(row["full_name"])
                            self.directorate_display.setText(row["directorate"])
                            self.staff_type_display.setText(row["staff_type"])
                            print(f"Staff details found: {row}")
                            return
                print(f"Error: Staff details not found for ID: {staff_id}")
            except FileNotFoundError:
                print("Error: staff_data.csv not found.")
            except Exception as e:
                print(f"Error populating staff details: {e}")

    def load_clock_in_data(self, filename):
        self.clock_in_data = {}
        print("Loading clock in data from file:", filename)
        try:
            with open(filename, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    timestamp = QDateTime.fromString(row["Timestamp"], "dd/MM/yyyy HH:mm:ss")
                    month_year = timestamp.toString("MMMM yyyy")
                    if month_year not in self.clock_in_data:
                        self.clock_in_data[month_year] = {"present": 0, "absent": 0}
                    
                    if row["Status"] == "present":
                        self.clock_in_data[month_year]["present"] += 1
                    else:
                        self.clock_in_data[month_year]["absent"] += 1
        except FileNotFoundError:
            print(f"Info: {filename} not found. Creating a new file.")
        except Exception as e:
            print(f"Error: {e}")

    def load_data_from_csv(self):
        try:
            with open(self.clock_in_data_filename, 'r') as file:
                reader = csv.reader(file)
                data = list(reader)
            print(f"Loaded data: {data}")
            return data
        except FileNotFoundError:
            print(f"Error: File '{self.clock_in_data_filename}' not found.")
            return []

    def draw_pie_chart(sizes, labels):
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.show()
    
    def calculate_percentages(self):
        present_count = 0
        late_count = 0
        absent_count = 0

        for entry in self.clock_in_data:
            if entry[4] == 'Present':
                present_count += 1
            elif entry[4] == 'Late':
                late_count += 1
            elif entry[4] == 'Absent':
                absent_count += 1
        
        total_count = present_count + late_count + absent_count

        if total_count == 0:
            print("No data available.")
            return 0, 0, 0

        present_percentage = (present_count / total_count) * 100
        late_percentage = (late_count / total_count) * 100
        absent_percentage = (absent_count / total_count) * 100

        print(f"Late count: {late_count}, Absent count: {absent_count}, Present count: {present_count}")
        print(f"Late percentage: {late_percentage}, Absent percentage: {absent_percentage}, Present percentage: {present_percentage}")

        return present_percentage, late_percentage, absent_percentage

    def generate_analytics(self):
        print(f"Loading data from: {self.clock_in_data_filename}")
        self.clock_in_data = self.load_data_from_csv()
        print(f"Loaded data: {self.clock_in_data}")
        
        present_count = 0
        late_count = 0
        absent_count = 0

        for entry in self.clock_in_data:
            if entry[4] == 'Late':
                late_count += 1
            elif entry[4] == 'Absent':
                absent_count += 1
            else:
                present_count += 1
        
        total_count = present_count + late_count + absent_count

        if total_count == 0:
            print("No data available.")
            return

        present_percentage = (present_count / total_count) * 100
        late_percentage = (late_count / total_count) * 100
        absent_percentage = (absent_count / total_count) * 100

        print(f"Late count: {late_count}, Absent count: {absent_count}, Present count: {present_count}")
        print(f"Late percentage: {late_percentage}, Absent percentage: {absent_percentage}, Present percentage: {present_percentage}")
        
        if present_count == 0 and late_count == 0 and absent_count == 0:
            print("All counts are zero. Cannot draw pie chart.")
            return

        print(f"Present percentage before creating dialog: {present_percentage}")
        print(f"Late percentage before creating dialog: {late_percentage}")
        print(f"Absent percentage before creating dialog: {absent_percentage}")

        print("Data for pie chart:", [present_count, late_count, absent_count])

        analytics_dialog = AnalyticsDialog(self.clock_in_data, present_percentage, late_percentage, absent_percentage)
        analytics_dialog.draw_pie()
        analytics_dialog.exec_()
    
    def open_search_dialog(self):
        search_dialog = SearchDialog(self)
        if search_dialog.exec_() == QDialog.Accepted:
            staff_id = search_dialog.search_id_input.text()
            start_date = search_dialog.start_date_edit.date().toString("dd/MM/yyyy")
            end_date = search_dialog.end_date_edit.date().toString("dd/MM/yyyy")

            try:
                start_date = datetime.strptime(start_date, "%d/%m/%Y")
                end_date = datetime.strptime(end_date, "%d/%m/%Y")
            except ValueError:
                QMessageBox.critical(self, "Error", "Incorrect date format. Please use dd/mm/yyyy.")
                return

            sanitized_staff_id = self.sanitize_staff_id(staff_id)
            file_path = f"{sanitized_staff_id}.csv"

            try:
                with open(file_path, mode='r') as file:
                    csv_reader = csv.DictReader(file)
                    results = []

                    for row in csv_reader:
                        if "Time" in row:
                            if len(row["Time"]) <= 8:
                                full_datetime_str = datetime.now().strftime("%d/%m/%Y") + " " + row["Time"]
                            else:
                                full_datetime_str = row["Time"]

                            clock_in_date = datetime.strptime(full_datetime_str, "%d/%m/%Y %H:%M:%S")
                            if start_date <= clock_in_date <= end_date:
                                results.append(row)

                    if results:
                        results_dialog = SearchResultsDialog(results, self)
                        results_dialog.exec_()
                    else:
                        QMessageBox.information(self, "No Records", "No records found for the given period.")

            except FileNotFoundError:
                QMessageBox.critical(self, "Error", f"No data found for staff ID {staff_id}")

    def sanitize_staff_id(self, staff_id):
        return staff_id.replace('/', '_')

    def clock_in(self):
        directorate = self.directorate_display.text()
        staff_type = self.staff_type_display.text()
        staff_id = self.id_input.text()
        sanitized_staff_id = self.sanitize_staff_id(staff_id)
        staff_name = self.staff_name_display.text().strip()
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")

        if staff_id:
            if not self.has_clocked_in(staff_id):
                current_time = datetime.now().time()
                if current_time <= time(hour=9, minute=10):
                    status = "Present"
                elif time(hour=9, minute=11) <= current_time <= time(hour=15, minute=59):
                    status = "Late"
                else:
                    status = "Absent"

                with open(self.clock_in_data_filename, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([staff_id, staff_name, directorate, staff_type, status, timestamp])
                print(f"{status.capitalize()} clock in successful.")
                self.show_clock_in_message(f"{staff_name} marked {status}.")

                staff_filename = f"{sanitized_staff_id}.csv"
                try:
                    file_exists = os.path.isfile(staff_filename)
                    with open(staff_filename, 'a', newline='') as file:
                        writer = csv.writer(file)
                        if not file_exists:
                            writer.writerow(["Date", "Staff Name", "Directorate", "Staff Type", "Status", "Time"])
                        writer.writerow([datetime.now().strftime("%d/%m/%Y"), staff_name, directorate, staff_type, status, timestamp])
                    print(f"Clock in data recorded for staff ID {staff_id} in {staff_filename}")
                except Exception as e:
                    print(f"Error writing to staff file {staff_filename}: {e}")

            else:
                print("Staff has already clocked in.")
                self.show_clock_in_message("Staff has already clocked in.")
        
        else:
            print("Please enter a staff ID.")
            self.show_clock_in_message("Please enter a staff ID.")

    def show_clock_in_message(self, message):
        self.clock_in_message_label.setText(message)

    def has_clocked_in(self, staff_id):
        try:
            with open(self.clock_in_data_filename, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == staff_id:
                        return True
        except FileNotFoundError:
            print("Error: Clock-in data file not found.")
        except Exception as e:
            print(f"Error: {e}")
        return False


    def validate_staff_id(self, staff_id, directorate, staff_type):
        try:
            with open("staff_data.csv", "r", encoding="utf-8-sig") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == staff_id and row[1] == directorate and row[2] == staff_type:
                        return True
        except FileNotFoundError:
            print("Error: staff_data.csv not found.")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
        return False

    def check_time(self):
        current_time = datetime.now().time()
        late_time_start = time(hour=9, minute=11)
        late_time_end = time(hour=15, minute=59)
        closing_time = time(hour=16)

        if current_time < closing_time:
            staff_ids = self.load_staff_ids()
            if not staff_ids:
                print("Error: No staff IDs found.")
                return

            try:
                with open(self.clock_in_data_filename, "r") as file:
                    reader = csv.reader(file)
                    clock_in_data = list(reader)
            except FileNotFoundError:
                print("Error: clock_in_data.csv not found.")
                return
            except Exception as e:
                print(f"Error: {e}")
                return

            staff_ids_clocked_in = set(row[0] for row in clock_in_data)
            late_staff = [row for row in clock_in_data if row[0] not in staff_ids_clocked_in and row[4] == "present"]
            late_staff_ids = [row[0] for row in late_staff if self.get_time(row[5]) > late_time_start]
            if late_staff_ids:
                self.mark_late(late_staff_ids)
                print("Late staff marked between 9:11 am and 3:59 pm.")
                clock_in_data = [row for row in clock_in_data if row[0] not in late_staff_ids]

                with open(self.clock_in_data_filename, "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerows(clock_in_data)
            else:
                print("No late staff between 9:11 am and 3:59 pm.")

        elif current_time >= closing_time:
            staff_ids = self.load_staff_ids()
            if not staff_ids:
                print("Error: No staff IDs found.")
                return

            try:
                with open(self.clock_in_data_filename, "r") as file:
                    reader = csv.reader(file)
                    clock_in_data = list(reader)
            except FileNotFoundError:
                print("Error: clock_in_data.csv not found.")
                return
            except Exception as e:
                print(f"Error: {e}")
                return

            staff_ids_clocked_in = set(row[0] for row in clock_in_data)
            absentees = [staff_id for staff_id in staff_ids if staff_id not in staff_ids_clocked_in]
            if absentees:
                self.mark_absentees(absentees)
                print("Absentees marked after 4:00 pm.")
            else:
                print("No absentees after 4:00 pm.")

    def get_time(self, timestamp):
        return datetime.strptime(timestamp, "%d/%m/%Y %H:%M:%S").time()
                
    def mark_absentees(self, absentees):
        try:
            current_date = datetime.now().strftime("%d-%m-%Y")
            file_name = f"clock_in_data_{current_date}.csv"
            with open(file_name, "a", newline="") as file:
                writer = csv.writer(file)
                for staff_id in absentees:
                    writer.writerow([staff_id, "", "", "", "Absent", ""])
            print(f"Absentees marked after 4:00 pm in '{file_name}'.")
            self.remove_absentees_from_data(absentees)
        except Exception as e:
            print(f"Error while marking absentees: {e}")

    def mark_late(self, late_staff):
        try:
            current_date = datetime.now().strftime("%d-%m-%Y")
            file_name = f"clock_in_data_{current_date}.csv"
            with open(file_name, "a", newline="") as file:
                writer = csv.writer(file)
                for staff_id in late_staff:
                    writer.writerow([staff_id, "", "", "", "Late", ""])
            print(f"Late staff marked between 9:11 am and 4:00 pm in '{file_name}'.")
            self.remove_late_from_data(late_staff)
        except Exception as e:
            print(f"Error while marking late staff: {e}")

    def load_staff_ids(self):
        staff_ids = []
        try:
            with open("staff_data.csv", "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                for row in reader:
                    staff_ids.append(row[0])
        except FileNotFoundError:
            print("Error: staff_data.csv not found.")
        except Exception as e:
            print(f"Error: {e}")
        return staff_ids

    def view_database(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Clock-in Data")
        dialog.setFixedSize(630, 300)
        layout = QVBoxLayout()

        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Staff ID", "Staff Name", "Directorate", "Staff Type", "Status", "Timestamp"])

        try:
            with open(self.clock_in_data_filename, "r", newline="") as file:
                reader = csv.reader(file)
                data = list(reader)
                table.setRowCount(len(data))
                for i, row in enumerate(data):
                    for j, value in enumerate(row):
                        item = QTableWidgetItem(value)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        table.setItem(i, j, item)
        except FileNotFoundError:
            print(f"Error: {self.clock_in_data_filename} not found.")

        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock_in_register = ClockInRegister()
    clock_in_register.show()
    sys.exit(app.exec_())