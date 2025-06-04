# ui/login.py

from ui.dashboard import DashboardWindow

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QFormLayout, QMessageBox,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
import sqlite3
import sys
import os


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hospital Management Login")
        self.setGeometry(600, 300, 400, 300)  # Bigger window for better layout
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)

        # Spacer top to push content vertically center
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Title Label
        title_label = QLabel("Login to Hospital Management System")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px ; color: #1abc9c;")
        main_layout.addWidget(title_label)

        # Form layout for inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(20)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumWidth(250)
        form_layout.addRow("Username:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumWidth(250)
        form_layout.addRow("Password:", self.password_input)

        main_layout.addLayout(form_layout)

        # Login Button
        login_btn = QPushButton("Login")
        login_btn.setFixedWidth(120)
        login_btn.clicked.connect(self.check_login)
        login_btn.setStyleSheet("margin-top: 20px;")
        main_layout.addWidget(login_btn, alignment=Qt.AlignCenter)

        # Spacer bottom for vertical centering
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(main_layout)

        # Apply dark theme styles
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #34495e;
                border: 1px solid #2980b9;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1abc9c;
            }
            QPushButton {
                background-color: #1abc9c;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
            QLabel {
                color: white;
            }
        """)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(BASE_DIR, 'db', 'hospital.db')
        conn = sqlite3.connect(db_path)

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            self.dashboard = DashboardWindow()
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.warning(self, "Failed", "Invalid username or password.")


# For testing directly
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
