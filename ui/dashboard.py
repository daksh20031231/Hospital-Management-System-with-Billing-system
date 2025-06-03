# ui/dashboard.py
from ui.billing import BillingWindow
from ui.patients import PatientWindow
from doctors import DoctorWindow
from ui.appointments import AppointmentWindow




from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
)

class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hospital Management - Dashboard")
        self.setGeometry(100, 100, 400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        label = QLabel("Welcome to the Hospital Management Dashboard")
        label.setStyleSheet("font-size: 16px; font-weight: bold;")

        # Buttons for features
        patients_btn = QPushButton("Manage Patients")
        patients_btn.clicked.connect(self.open_patients)
        doctors_btn = QPushButton("Manage Doctors")
        doctors_btn.clicked.connect(self.open_doctors)
        appointments_btn = QPushButton("Manage Appointments")
        appointments_btn.clicked.connect(self.open_appointments)
        billing_btn = QPushButton("Billing")
        billing_btn.clicked.connect(self.open_billing)
        logout_btn = QPushButton("Logout")

        logout_btn.clicked.connect(self.logout)

        # Add widgets to layout
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
