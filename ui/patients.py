from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableWidget,
    QTableWidgetItem, QHBoxLayout
)
import sqlite3
import os

class PatientWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Patients")
        self.setGeometry(150, 150, 600, 500)
        self.selected_patient_id = None
        self.setup_ui()
        self.load_patients()


    def setup_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.gender_input = QLineEdit()
        self.contact_input = QLineEdit()

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Age:", self.age_input)
        form_layout.addRow("Gender:", self.gender_input)
        form_layout.addRow("Contact:", self.contact_input)

        self.add_btn = QPushButton("Add Patient")
        self.add_btn.clicked.connect(self.add_or_update_patient)

        layout.addLayout(form_layout)
        layout.addWidget(self.add_btn)

        # Table for displaying patients
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Gender", "Contact", "Actions"])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def get_db_path(self):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db', 'hospital.db'))

    def load_patients(self):
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)

        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)
            for col_idx, col_val in enumerate(row[:5]):  # Only set columns 0 to 4
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_val)))

            # Action buttons
            edit_btn = QPushButton("Edit")
            delete_btn = QPushButton("Delete")
            edit_btn.clicked.connect(lambda _, r=row: self.load_for_edit(r))
            delete_btn.clicked.connect(lambda _, pid=row[0]: self.delete_patient(pid))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 0, 5, 0)
            action_layout.setSpacing(10)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row_idx, 5, action_widget)

            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()

    def add_or_update_patient(self):
        name = self.name_input.text()
        age = self.age_input.text()
        gender = self.gender_input.text()
        contact = self.contact_input.text()

        if not name or not age:
            QMessageBox.warning(self, "Error", "Name and age are required.")
            return

        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()

        if self.selected_patient_id:
            # Update patient
            cursor.execute("""
                UPDATE patients
                SET name=?, age=?, gender=?, contact=?
                WHERE id=?
            """, (name, age, gender, contact, self.selected_patient_id))
            self.add_btn.setText("Add Patient")
            self.selected_patient_id = None
        else:
            # Add new patient
            cursor.execute("""
                INSERT INTO patients (name, age, gender, contact)
                VALUES (?, ?, ?, ?)
            """, (name, age, gender, contact))

        conn.commit()
        conn.close()
        self.clear_form()
        self.load_patients()
        QMessageBox.information(self, "Success", "Patient saved successfully.")

    def delete_patient(self, patient_id):
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this patient?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            cursor.execute("DELETE FROM patients WHERE id=?", (patient_id,))
            conn.commit()
            conn.close()
            self.load_patients()

    def load_for_edit(self, row):
        self.selected_patient_id = row[0]
        self.name_input.setText(row[1])
        self.age_input.setText(str(row[2]))
        self.gender_input.setText(row[3])
        self.contact_input.setText(row[4])
        self.add_btn.setText("Update Patient")

    def clear_form(self):
        self.name_input.clear()
        self.age_input.clear()
        self.gender_input.clear()
        self.contact_input.clear()
