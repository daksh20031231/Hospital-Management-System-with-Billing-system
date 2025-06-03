from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QHBoxLayout, QComboBox
)

import sqlite3
import os


class AppointmentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Appointments")
        self.setGeometry(200, 200, 700, 500)
        self.selected_appointment_id = None
        self.setup_ui()
        self.load_appointments()

    def get_db_path(self):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db', 'hospital.db'))

    def setup_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        # Patient input (ID or Name)
        self.patient_input = QLineEdit()
        self.patient_input.textChanged.connect(self.show_patient_details)  # connect text change
        form_layout.addRow("Patient ID:", self.patient_input)

        # Label to show patient details dynamically
        self.patient_details_label = QLabel("")
        form_layout.addRow("Patient Details:", self.patient_details_label)

        self.doctor_combo = QComboBox()
        form_layout.addRow("Doctor:", self.doctor_combo)

        self.date_input = QLineEdit()
        form_layout.addRow("Date (YYYY-MM-DD):", self.date_input)

        self.time_input = QLineEdit()
        form_layout.addRow("Time (HH:MM):", self.time_input)

        self.purpose_input = QLineEdit()
        form_layout.addRow("Purpose:", self.purpose_input)

        self.load_doctor_list()

        self.add_btn = QPushButton("Add Appointment")
        self.add_btn.clicked.connect(self.add_or_update_appointment)

        layout.addLayout(form_layout)
        layout.addWidget(self.add_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Patient", "Contact", "Doctor", "Date", "Time", "Purpose"])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_doctor_list(self):
        db = sqlite3.connect(self.get_db_path())
        cursor = db.cursor()

        self.doctor_combo.clear()
        cursor.execute("SELECT id, name FROM doctors")
        self.doctors = cursor.fetchall()
        for d in self.doctors:
            self.doctor_combo.addItem(d[1], d[0])

        db.close()

    def load_appointments(self):
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, p.name, p.contact, d.name, a.date, a.time, a.purpose
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
        """)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)

        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)
            # Set data for columns 0 to 6 (7 columns)
            for col_idx, val in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))

            # Add buttons in last column (index 6) – shift buttons to separate column
            reschedule_btn = QPushButton("Reschedule")
            delete_btn = QPushButton("Delete")
            done_btn = QPushButton("Done")

            reschedule_btn.clicked.connect(lambda _, r=row: self.reschedule_appointment(r))
            delete_btn.clicked.connect(lambda _, id=row[0]: self.delete_appointment(id))
            done_btn.clicked.connect(lambda _, id=row[0]: self.mark_done_appointment(id))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 0, 5, 0)
            action_layout.setSpacing(5)
            action_layout.addWidget(reschedule_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addWidget(done_btn)

            # Instead of overwriting Purpose column, add buttons to next column (7th)
            # So we need one more column or change table to 8 columns
            # To keep it simple, let's add buttons in last column 7 (so increase column count to 8)
            # Or put buttons in the Purpose column (index 6) as before
            # Since you want contact shown, we have 7 columns for data; put buttons in a new 8th column.

            # So change column count to 8:
            # Update this in setup_ui and here accordingly

            # But since you requested only to show contact in appointment list, let's put buttons in column 7.
            # So let's increase column count to 8 in setup_ui and add header for actions

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    # To fix buttons placement correctly, update setup_ui and load_appointments column counts and headers as below:

    def setup_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.patient_input = QLineEdit()
        self.patient_input.textChanged.connect(self.show_patient_details)
        form_layout.addRow("Patient ID:", self.patient_input)

        self.patient_details_label = QLabel("")
        form_layout.addRow("Patient Details:", self.patient_details_label)

        self.doctor_combo = QComboBox()
        form_layout.addRow("Doctor:", self.doctor_combo)

        self.date_input = QLineEdit()
        form_layout.addRow("Date (YYYY-MM-DD):", self.date_input)

        self.time_input = QLineEdit()
        form_layout.addRow("Time (HH:MM):", self.time_input)

        self.purpose_input = QLineEdit()
        form_layout.addRow("Purpose:", self.purpose_input)

        self.load_doctor_list()

        self.add_btn = QPushButton("Add Appointment")
        self.add_btn.clicked.connect(self.add_or_update_appointment)

        layout.addLayout(form_layout)
        layout.addWidget(self.add_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Patient", "Contact", "Doctor", "Date", "Time", "Purpose", "Actions"])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_appointments(self):
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, p.name, p.contact, d.name, a.date, a.time, a.purpose
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
        """)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)

        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)
            for col_idx, val in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))

            reschedule_btn = QPushButton("Reschedule")
            delete_btn = QPushButton("Delete")
            done_btn = QPushButton("Done")

            delete_btn = QPushButton("Delete")
            done_btn = QPushButton("Done")

            delete_btn.clicked.connect(lambda _, id=row[0]: self.delete_appointment(id))
            done_btn.clicked.connect(lambda _, id=row[0]: self.mark_done_appointment(id))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 0, 5, 0)
            action_layout.setSpacing(5)
            action_layout.addWidget(delete_btn)
            action_layout.addWidget(done_btn)

            self.table.setCellWidget(row_idx, 7, action_widget)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def show_patient_details(self):
        input_text = self.patient_input.text().strip()
        if not input_text:
            self.patient_details_label.setText("")
            return

        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()

        if input_text.isdigit():
            cursor.execute("SELECT id, name, age, contact FROM patients WHERE id=?", (int(input_text),))
        else:
            cursor.execute("SELECT id, name, age, contact FROM patients WHERE LOWER(name)=?", (input_text.lower(),))

        patient = cursor.fetchone()
        conn.close()

        if patient:
            details = f"ID: {patient[0]}, Name: {patient[1]}, Age: {patient[2]}, Contact: {patient[3]}"
            self.patient_details_label.setText(details)
        else:
            self.patient_details_label.setText("No patient found.")

    def add_or_update_appointment(self):
        patient_text = self.patient_input.text().strip()
        doctor_id = self.doctor_combo.currentData()
        date = self.date_input.text().strip()
        time = self.time_input.text().strip()
        purpose = self.purpose_input.text().strip()

        if not patient_text or not date or not time or not purpose:
            QMessageBox.warning(self, "Missing Fields", "Please fill in all details.")
            return

        patient_id = self.get_patient_id_from_input(patient_text)
        if not patient_id:
            QMessageBox.warning(self, "Invalid Patient", "Patient not found with given ID or name.")
            return

        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, date, time, purpose)
            VALUES (?, ?, ?, ?, ?)
        """, (patient_id, doctor_id, date, time, purpose))

        conn.commit()
        conn.close()

        self.clear_form()
        self.load_appointments()
        QMessageBox.information(self, "Success", "Appointment added successfully.")

    def get_patient_id_from_input(self, input_text):
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()

        if input_text.isdigit():
            cursor.execute("SELECT id FROM patients WHERE id=?", (int(input_text),))
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0]
            else:
                return None
        else:
            cursor.execute("SELECT id FROM patients WHERE LOWER(name)=?", (input_text.lower(),))
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0]
            else:
                return None

    def clear_form(self):
        self.patient_input.clear()
        self.patient_details_label.clear()  # clear patient details on reset
        self.date_input.clear()
        self.time_input.clear()
        self.purpose_input.clear()
        self.add_btn.setText("Add Appointment")
        self.selected_appointment_id = None

    def reschedule_appointment(self, appointment_row):
        appointment_id = appointment_row[0]
        print(f"Reschedule appointment ID: {appointment_id}")

    def delete_appointment(self, appointment_id):
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this appointment?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            cursor.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
            conn.commit()
            conn.close()
            self.load_appointments()

    def mark_done_appointment(self, appointment_id):
        confirm = QMessageBox.question(
            self, "Mark Done",
            "Mark this appointment as done and remove from the list?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            cursor.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
            conn.commit()
            conn.close()
            self.load_appointments()
