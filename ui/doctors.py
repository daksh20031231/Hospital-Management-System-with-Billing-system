from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QHeaderView
)
from PyQt5.QtCore import Qt
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
        self.setStyleSheet("""
            QWidget {
                background-color: #1e272e;
                color: #f5f6fa;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #485460;
                border-radius: 5px;
                font-size: 14px;
                background-color: #2f3640;
                color: #f5f6fa;
            }
            QPushButton {
                padding: 8px 14px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton#mainButton {
                background-color: #00b894;
                color: white;
            }
            QPushButton#mainButton:hover {
                background-color: #019875;
            }
            QPushButton#editButton {
                background-color: #3498db;
                color: white;
            }
            QPushButton#deleteButton {
                background-color: #e74c3c;
                color: white;
            }
            QTableWidget {
                background-color: #2f3640;
                alternate-background-color: #3b3f46;
                gridline-color: #7f8c8d;
                color: #f5f6fa;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #273c75;
                color: white;
                padding: 6px;
                border: 1px solid #192a56;
            }
        """)

        layout = QVBoxLayout()

        # Fix title label rendering
        title = QLabel()
        title.setText("‍⚕<b>Manage Doctors</b>")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #00cec9;
            font-size: 24px;
            font-weight: bold;
            padding: 16px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)

        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.specialization_input = QLineEdit()
        self.email_input = QLineEdit()
        self.contact_input = QLineEdit()

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Specialization:", self.specialization_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Contact:", self.contact_input)

        layout.addLayout(form_layout)

        self.add_btn = QPushButton("Add Doctor")
        self.add_btn.setObjectName("mainButton")
        self.add_btn.clicked.connect(self.add_or_update_doctor)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Table for displaying doctors
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Specialization", "Email", "Contact", "Actions"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)

        layout.addSpacing(20)
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
            edit_btn.setObjectName("editButton")
            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("deleteButton")

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
