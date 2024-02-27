import sys
import csv
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QComboBox,
                             QLineEdit, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,)
from PyQt5.QtCore import QDateTime, QTimer
import pyqtgraph as pg
from datetime import datetime

class ClockInRegister(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clock-in Register")
        self.setGeometry(100, 100, 800, 600)

        self.setStyleSheet("background-color: white;")

        self.staff_name_label = QLabel("Staff Name:", self)
        self.staff_name_label.move(50, 50)
        self.staff_name_label.setStyleSheet("color: darkgreen; font-weight: bold;")

        self.staff_name_combo = QComboBox(self)
        self.staff_name_combo.move(150, 50)
        self.staff_name_combo.currentIndexChanged.connect(self.populate_staff_details)
        self.staff_name_combo.setStyleSheet("background-color: white; border: 1px solid darkgreen;")

        self.directorate_label = QLabel("Directorate:", self)
        self.directorate_label.move(50, 100)
        self.directorate_label.setStyleSheet("color: darkgreen; font-weight: bold;")

        self.directorate_combo = QComboBox(self)
        self.directorate_combo.move(150, 100)
        self.directorate_combo.setStyleSheet("background-color: white; border: 1px solid darkgreen;")

        self.staff_type_label = QLabel("Staff Type:", self)
        self.staff_type_label.move(50, 150)
        self.staff_type_label.setStyleSheet("color: darkgreen; font-weight: bold;")

        self.staff_type_combo = QComboBox(self)
        self.staff_type_combo.move(150, 150)
        self.staff_type_combo.setStyleSheet("background-color: white; border: 1px solid darkgreen;")

        self.id_label = QLabel("Staff ID:", self)
        self.id_label.move(50, 200)
        self.id_label.setStyleSheet("color: darkgreen; font-weight: bold;")

        self.id_input = QLineEdit(self)
        self.id_input.move(150, 200)
        self.id_input.setStyleSheet("background-color: white; border: 1px solid darkgreen;")

        self.clock_in_button = QPushButton("Clock In", self)
        self.clock_in_button.move(150, 250)
        self.clock_in_button.clicked.connect(self.clock_in)
        self.clock_in_button.setStyleSheet("background-color: darkgreen; color: white; border: none; padding: 5px 10px; font-weight: bold;")

        self.view_db_button = QPushButton("View Database", self)
        self.view_db_button.move(250, 250)
        self.view_db_button.clicked.connect(self.view_database)
        self.view_db_button.setStyleSheet("background-color: darkgreen; color: white; border: none; padding: 5px 10px; font-weight: bold;")

        self.plot_widget = pg.PlotWidget(title="Monthly Statistics")
        self.plot_widget.move(50, 300)
        self.plot_widget.resize(600, 300)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_time)
        self.timer.start(60000)

        self.load_staff_names_from_csv("staff_data.csv")
        self.populate_staff_details()

        self.clock_in_data_filename = f"clock_in_data_{datetime.now().strftime('%d-%m-%Y')}.csv"
        self.load_clock_in_data(self.clock_in_data_filename)
        self.calculate_monthly_statistics()
        self.plot_statistics()

    def load_staff_names_from_csv(self, filename):
        try:
            with open(filename, "r") as file:
                reader = csv.DictReader(file)
                staff_names = [row["full_name"] for row in reader]
                self.staff_name_combo.addItems(staff_names)
                print("Staff names loaded successfully:", staff_names)
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
        except Exception as e:
            print(f"Error loading staff names: {e}")

    def populate_staff_details(self):
        staff_name = self.staff_name_combo.currentText().strip().lower()
        print("Staff name:", staff_name)
        if staff_name:
            try:
                with open("staff_data.csv", "r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        print("Row:", row)
                        csv_staff_name = row["full_name"].strip().lower()
                        print("Comparing:", csv_staff_name)
                        if csv_staff_name == staff_name:
                            staff_id = row["\ufeffstaff_id"]
                            self.id_input.setText(staff_id)
                            self.directorate_combo.setCurrentText(row["directorate"])
                            self.populate_staff_types(row["directorate"])
                            self.staff_type_combo.setCurrentText(row["staff_type"])
                            print(f"Staff details found: {row}")
                            return
            except FileNotFoundError:
                print("Error: staff_data.csv not found.")
            except Exception as e:
                print(f"Error populating staff details: {e}")

        print(f"Error: Staff details not found for: {staff_name}")


    def populate_staff_types(self, directorate):
        # directorate = self.directorate_combo.currentText()
        staff_types = self.load_staff_types(directorate)

        self.staff_type_combo.clear()

        if staff_types:
            self.staff_type_combo.addItems(staff_types)
        else:
            self.staff_type_combo.addItem("No staff types found")

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
        self.clock_in_data = defaultdict(lambda: {"present": 0, "absent": 0})
        print("Loading clock in data from file:", filename)
        try:
            with open(filename, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    timestamp = QDateTime.fromString(row["timestamp"], "dd/MM/yyyy HH:mm:ss")
                    month_year = timestamp.toString("MMMM yyyy")
                    if row["status"] == "present":
                        self.clock_in_data[month_year]["present"] += 1
                    else:
                        self.clock_in_data[month_year]["absent"] += 1
        except FileNotFoundError:
            print(f"Info: {filename} not found. Creating a new file.")
        except Exception as e:
            print(f"Error: {e}")

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
        directorate = self.directorate_combo.currentText()
        staff_type = self.staff_type_combo.currentText()
        staff_id = self.id_input.text()
        timestamp = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss")

        if staff_id:
            if self.validate_staff_id(staff_id, directorate, staff_type):
                with open(self.clock_in_data_filename, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([staff_id, directorate, staff_type, "present", timestamp])
                print("Clock in successful.")
            else:
                print("Invalid staff ID, directorate, or staff type.")
        else:
            print("Please enter a staff ID.")

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
        current_time = QDateTime.currentDateTime().toString("HH:mm")

        if current_time > "09:10":
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
            tardy_staff = [row[0] for row in clock_in_data if row[0] not in staff_ids_clocked_in and row[4].split()[1] > "09:10"]
            absentees = [staff_id for staff_id in staff_ids if staff_id not in staff_ids_clocked_in]

            if absentees:
                self.mark_absentees(absentees)
                print("Absentees marked after 9:10 am.")
            else:
                print("No absentees after 9:10 am.")
            
            if tardy_staff:
                self.mark_tardy(tardy_staff)
                print("Tardy staff marked between 9:11 am and 12:00 pm.")
            else:
                print("No tardy staff between 9:11 am and 12:00 pm.")

    def mark_absentees(self, absentees):
        try:
            current_date = datetime.now().strftime("%d/%m/%Y")
            file_name = f"absentees_{current_date}.csv"
            with open(file_name, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Staff ID"])
                for staff_id in absentees:
                    writer.writerow([staff_id])
            print("Absentees marked after 9:10 am. Check 'absentees.csv' for details.")
        except Exception as e:
            print(f"Error while marking absentees: {e}")

    def mark_tardy(self, tardy_staff):
        try:
            current_date = datetime.now().strftime("%d/%m/%Y")
            file_name = f"tardy_{current_date}.csv"
            with open(file_name, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Staff ID"])
                for staff_id in tardy_staff:
                    writer.writerow([staff_id])
            print("Tardy staff marked between 9:11 am and 12:00 pm. Check 'tardy.csv' for details.")
        except Exception as e:
            print(f"Error while marking tardy staff: {e}")

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
        layout = QVBoxLayout()

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Staff ID", "Directorate", "Staff Type", "Status", "Timestamp"])

        try:
            with open(self.clock_in_data_filename, "r", newline="") as file:
                reader = csv.reader(file)
                data = list(reader)
                table.setRowCount(len(data))
                for i, row in enumerate(data):
                    for j, value in enumerate(row):
                        table.setItem(i, j, QTableWidgetItem(value))
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
