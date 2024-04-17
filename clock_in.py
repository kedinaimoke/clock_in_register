import sys
import csv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QComboBox,
                             QLineEdit, QDialog, QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QMessageBox, QDialogButtonBox)
from PyQt5.QtCore import QDateTime, QTimer, Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
import pyqtgraph as pg
from datetime import datetime, time

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

        # If staff ID is provided, remove the data
        self.remove_staff()

    def remove_staff(self):
        rows = self.table_widget.rowCount()
        for row in range(rows):
            if self.table_widget.item(row, 0).text() == self.staff_id_input.text():
                self.table_widget.removeRow(row)
                break

        # Remove the staff from the CSV file
        with open("staff_data.csv", "r") as file:
            lines = file.readlines()

        with open("staff_data.csv", "w") as file:
            for line in lines:
                if self.staff_id_input.text() not in line:
                    file.write(line)

        QMessageBox.information(self, "Success", "Staff removed successfully.")
        self.accept()
class ClockInRegister(QMainWindow):
    def __init__(self):
        super().__init__()
        self.login_dialog = LoginDialog()
        if not self.login_dialog.exec_():
            sys.exit(1)
        
        self.setWindowTitle("Clock-in Register")
        self.setGeometry(200, 100, 800, 600)
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

        self.staff_name_label = QLabel("Staff Name:", self)
        self.staff_name_label.setGeometry(x_offset, 300, 100, input_height)
        self.staff_name_label.setStyleSheet("color: darkgreen; font-weight: bold;")

        self.staff_name_combo = QComboBox(self)
        self.staff_name_combo.setGeometry(x_offset + 100 + input_margin, 300, input_width, input_height)
        self.staff_name_combo.currentIndexChanged.connect(self.populate_staff_details)
        self.staff_name_combo.setStyleSheet("background-color: white; border: 1px solid darkgreen;")

        self.directorate_label = QLabel("Directorate:", self)
        self.directorate_label.setGeometry(x_offset, 350, 100, input_height)
        self.directorate_label.setStyleSheet("color: darkgreen; font-weight: bold;")

        self.directorate_display = QLabel(self)
        self.directorate_display.setGeometry(x_offset + 100 + input_margin, 350, input_width, input_height)
        self.directorate_display.setStyleSheet("background-color: white; border: 1px solid darkgreen; padding: 2px;")

        self.staff_type_label = QLabel("Staff Type:", self)
        self.staff_type_label.setGeometry(x_offset, 400, 100, input_height)
        self.staff_type_label.setStyleSheet("color: darkgreen; font-weight: bold;")

        self.staff_type_display = QLabel(self)
        self.staff_type_display.setGeometry(x_offset + 100 + input_margin, 400, input_width, input_height)
        self.staff_type_display.setStyleSheet("background-color: white; border: 1px solid darkgreen; padding: 2px;")

        self.id_label = QLabel("Staff ID:", self)
        self.id_label.setGeometry(x_offset, 450, 100, input_height)
        self.id_label.setStyleSheet("color: darkgreen; font-weight: bold;")

        self.id_input = QLineEdit(self)
        self.id_input.setGeometry(x_offset + 100 + input_margin, 450, input_width, input_height)
        self.id_input.setStyleSheet("background-color: white; border: 1px solid darkgreen;")
        self.id_input.setReadOnly(True)

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

        self.load_staff_names_from_csv("staff_data.csv")
        self.populate_staff_details()

        self.clock_in_data_filename = f"clock_in_data_{datetime.now().strftime('%d-%m-%Y')}.csv"
        self.load_clock_in_data(self.clock_in_data_filename)
        self.calculate_monthly_statistics()
        self.plot_statistics()

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
                        # item.setFlags(item.flags() & ~Qt.ItemIsEditable)
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

        # layout.addWidget(add_new_button)
        # layout.addWidget(button_box)
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
        staff_name = self.staff_name_combo.currentText().strip()
        print("Staff name:", staff_name)
        if staff_name:
            try:
                with open("staff_data.csv", "r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        print("Row:", row)
                        csv_staff_name = row["full_name"].strip()
                        print("Comparing:", csv_staff_name)
                        if csv_staff_name == staff_name:
                            staff_id = row["staff_id"]
                            self.id_input.setText(staff_id)
                            directorate = row["directorate"].strip()
                            # self.directorate_display.addItem(directorate)
                            self.directorate_display.setText(directorate)
                            self.populate_staff_types(directorate)
                            self.staff_type_display.setText(row["staff_type"])
                            print(f"Staff details found: {row}")
                            return
                print(f"Error: Staff details not found for: {staff_name}")
            except FileNotFoundError:
                print("Error: staff_data.csv not found.")
            except Exception as e:
                print(f"Error populating staff details: {e}")


    def populate_staff_types(self, directorate):
        # directorate = self.directorate_combo.currentText()
        staff_types = self.load_staff_types(directorate)

        # self.staff_type_combo.clear()
        if staff_types:
            self.staff_type_display.setText(", ".join(staff_types))
        else:
            self.staff_type_display.setText("No staff types found")

    def load_staff_types(self, directorate):
        staff_types = set()
        try:
            with open("staff_data.csv", "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["directorate"] == directorate:
                        staff_types.add(row["staff_type"])
        except FileNotFoundError:
            print("Error: staff_data.csv not found.")
        except Exception as e:
            print(f"Error: {e}")

        return list(staff_types)

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

    def generate_analytics(self):
        self.calculate_monthly_statistics()
        self.plot_statistics()

    def calculate_monthly_statistics(self):
        self.months = sorted(self.clock_in_data.keys())
        self.present_percentages = [self.clock_in_data[month]["present"] / (self.clock_in_data[month]["present"] + self.clock_in_data[month]["absent"]) * 100 for month in self.months]
        self.absent_percentages = [self.clock_in_data[month]["absent"] / (self.clock_in_data[month]["present"] + self.clock_in_data[month]["absent"]) * 100 for month in self.months]

    def plot_statistics(self):
        self.plot_widget.clear()
        self.plot_widget.addLegend()
        self.plot_widget.setLabel("left", "Percentage", units="%")
        self.plot_widget.setLabel("bottom", "Month")
        self.plot_widget.setXRange(0, len(self.months), padding=0.1)
        
        x_labels = [(i, month) for i, month in enumerate(self.months)]
        self.plot_widget.getAxis("bottom").setTicks([x_labels])

        self.plot_widget.plot(range(len(self.months)), self.present_percentages, pen=None, symbol='o', symbolSize=10, name="Present Percentage", fillLevel=0)
        self.plot_widget.plot(range(len(self.months)), self.absent_percentages, pen=None, symbol='s', symbolSize=10, name="Absent Percentage", fillLevel=0)

    def clock_in(self):
        directorate = self.directorate_display.text()
        staff_type = self.staff_type_display.text()
        staff_id = self.id_input.text()
        staff_name = self.staff_name_combo.currentText()
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
            else:
                print("Staff has already clocked in.")
                self.show_clock_in_message("Staff has already clocked in.")
        else:
            print("Please enter a staff name.")

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