# ui/dashboard.py
from ui.billing import BillingWindow
from ui.patients import PatientWindow
from ui.doctors import DoctorWindow
from ui.appointments import AppointmentWindow

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt

class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hospital Management - Dashboard")
        self.setGeometry(100, 100, 450, 400)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 40, 50, 40)

        label = QLabel("Welcome to the Hospital Management Dashboard")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 30px;
        """)

        # Create buttons with consistent styling
        btn_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """

        patients_btn = QPushButton("Manage Patients")
        patients_btn.setStyleSheet(btn_style)
        patients_btn.clicked.connect(self.open_patients)
        patients_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        doctors_btn = QPushButton("Manage Doctors")
        doctors_btn.setStyleSheet(btn_style)
        doctors_btn.clicked.connect(self.open_doctors)
        doctors_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        appointments_btn = QPushButton("Manage Appointments")
        appointments_btn.setStyleSheet(btn_style)
        appointments_btn.clicked.connect(self.open_appointments)
        appointments_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        billing_btn = QPushButton("Billing")
        billing_btn.setStyleSheet(btn_style)
        billing_btn.clicked.connect(self.open_billing)
        billing_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        logout_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Add widgets to layout in order
        layout.addWidget(label)
        layout.addWidget(patients_btn)
        layout.addWidget(doctors_btn)
        layout.addWidget(appointments_btn)
        layout.addWidget(billing_btn)
        layout.addWidget(logout_btn)

        self.setLayout(layout)

    def open_patients(self):
        self.patients_window = PatientWindow()
        self.patients_window.show()

    def open_doctors(self):
        self.doctors_window = DoctorWindow()
        self.doctors_window.show()

    def open_appointments(self):
        self.appointments_window = AppointmentWindow()
        self.appointments_window.show()

    def open_billing(self):
        self.billing_window = BillingWindow()
        self.billing_window.show()

    def logout(self):
        QMessageBox.information(self, "Logout", "You have been logged out.")
        self.close()
