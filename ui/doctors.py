from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableWidget,
    QTableWidgetItem, QHBoxLayout
)
import sqlite3
import os

class DoctorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Doctors")
        self.setGeometry(150, 150, 600, 500)
        self.selected_doctor_id = None
        self.setup_ui()
        self.load_doctors()

    def setup_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.specialization_input = QLineEdit()
        self.email_input = QLineEdit()
        self.contact_input = QLineEdit()

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Specialization:", self.specialization_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Contact:", self.contact_input)

        self.add_btn = QPushButton("Add Doctor")
        self.add_btn.clicked.connect(self.add_or_update_doctor)

        layout.addLayout(form_layout)
        layout.addWidget(self.add_btn)

        # Table for displaying doctors
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Specialization", "Email", "Contact", "Actions"])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def get_db_path(self):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db', 'hospital.db'))

    def load_doctors(self):
        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors")
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
            delete_btn.clicked.connect(lambda _, did=row[0]: self.delete_doctor(did))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 0, 5, 0)
            action_layout.setSpacing(10)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row_idx, 5, action_widget)

            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()

    def add_or_update_doctor(self):
        name = self.name_input.text()
        specialization = self.specialization_input.text()
        email = self.email_input.text()
        contact = self.contact_input.text()

        if not name or not specialization:
            QMessageBox.warning(self, "Error", "Name and specialization are required.")
            return

        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()

        if self.selected_doctor_id:
            # Update doctor
            cursor.execute("""
                UPDATE doctors
                SET name=?, specialization=?, email=?, contact=?
                WHERE id=?
            """, (name, specialization, email, contact, self.selected_doctor_id))
            self.add_btn.setText("Add Doctor")
            self.selected_doctor_id = None
        else:
            # Add new doctor
            cursor.execute("""
                INSERT INTO doctors (name, specialization, email, contact)
                VALUES (?, ?, ?, ?)
            """, (name, specialization, email, contact))

        conn.commit()
        conn.close()
        self.clear_form()
        self.load_doctors()
        QMessageBox.information(self, "Success", "Doctor saved successfully.")

    def delete_doctor(self, doctor_id):
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this doctor?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            cursor.execute("DELETE FROM doctors WHERE id=?", (doctor_id,))
            conn.commit()
            conn.close()
            self.load_doctors()

    def load_for_edit(self, row):
        self.selected_doctor_id = row[0]
        self.name_input.setText(row[1])
        self.specialization_input.setText(row[2])
        self.email_input.setText(row[3])
        self.contact_input.setText(row[4])
        self.add_btn.setText("Update Doctor")

    def clear_form(self):
        self.name_input.clear()
        self.specialization_input.clear()
        self.email_input.clear()
        self.contact_input.clear()
