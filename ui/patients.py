from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QHeaderView
)
from PyQt5.QtCore import Qt
import sqlite3
import os


class PatientWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Patients")
        self.setGeometry(150, 150, 800, 600)
        self.selected_patient_id = None
        self.setup_ui()
        self.load_patients()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e272e;
                color: #f5f6fa;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                font-size: 20px;
                font-weight: bold;
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

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.gender_input = QLineEdit()
        self.contact_input = QLineEdit()

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Age:", self.age_input)
        form_layout.addRow("Gender:", self.gender_input)
        form_layout.addRow("Contact:", self.contact_input)

        main_layout.addWidget(QLabel("🩺 Manage Patients"), alignment=Qt.AlignCenter)
        main_layout.addLayout(form_layout)

        self.add_btn = QPushButton("Add Patient")
        self.add_btn.setObjectName("mainButton")
        self.add_btn.clicked.connect(self.add_or_update_patient)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Gender", "Contact", "Actions"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)

        main_layout.addSpacing(20)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

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
            for col_idx, col_val in enumerate(row[:5]):
                item = QTableWidgetItem(str(col_val))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row_idx, col_idx, item)

            edit_btn = QPushButton("Edit")
            edit_btn.setObjectName("editButton")
            edit_btn.clicked.connect(lambda _, r=row: self.load_for_edit(r))

            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("deleteButton")
            delete_btn.clicked.connect(lambda _, pid=row[0]: self.delete_patient(pid))

            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(8)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)

            self.table.setCellWidget(row_idx, 5, action_widget)

    def add_or_update_patient(self):
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        gender = self.gender_input.text().strip()
        contact = self.contact_input.text().strip()

        if not name or not age:
            QMessageBox.warning(self, "Error", "Name and age are required.")
            return

        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()

        if self.selected_patient_id:
            cursor.execute("""
                UPDATE patients
                SET name=?, age=?, gender=?, contact=?
                WHERE id=?
            """, (name, age, gender, contact, self.selected_patient_id))
            self.add_btn.setText("Add Patient")
            self.selected_patient_id = None
        else:
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
