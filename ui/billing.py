from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QLabel, QHBoxLayout, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QTextDocument, QPixmap
import sqlite3
import os
import datetime


class BillingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Billing")
        self.setGeometry(250, 250, 700, 500)
        self.services = []
        self.setup_ui()

    def get_db_path(self):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db', 'hospital.db'))

    def get_logo_path(self):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png'))

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.patient_input = QLineEdit()
        self.patient_input.textChanged.connect(self.load_patient_info)
        form_layout.addRow("Patient ID or Name:", self.patient_input)

        self.patient_details_label = QLabel("")
        form_layout.addRow("Patient Info:", self.patient_details_label)

        layout.addLayout(form_layout)

        self.services_table = QTableWidget()
        self.services_table.setColumnCount(3)
        self.services_table.setHorizontalHeaderLabels(["Service", "Quantity", "Price"])
        layout.addWidget(self.services_table)

        add_service_btn = QPushButton("Add Service")
        add_service_btn.clicked.connect(self.add_service_row)
        layout.addWidget(add_service_btn)

        self.total_label = QLabel("Total: ₹0.00")
        layout.addWidget(self.total_label)

        generate_btn = QPushButton("Generate Bill")
        generate_btn.clicked.connect(self.generate_bill)
        layout.addWidget(generate_btn)

        self.setLayout(layout)

    def load_patient_info(self):
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
            self.patient_id = patient[0]
            self.patient_details_label.setText(f"ID: {patient[0]}, Name: {patient[1]}, Age: {patient[2]}, Contact: {patient[3]}")
        else:
            self.patient_id = None
            self.patient_details_label.setText("No patient found.")

    def add_service_row(self):
        row = self.services_table.rowCount()
        self.services_table.insertRow(row)

        self.services_table.setItem(row, 0, QTableWidgetItem(""))  # Service
        self.services_table.setItem(row, 1, QTableWidgetItem("1"))  # Quantity
        self.services_table.setItem(row, 2, QTableWidgetItem("0.00"))  # Price

    def generate_bill(self):
        if not hasattr(self, 'patient_id') or not self.patient_id:
            QMessageBox.warning(self, "Invalid Patient", "Please select a valid patient.")
            return

        total = 0.0
        services = []

        for row in range(self.services_table.rowCount()):
            service_item = self.services_table.item(row, 0)
            qty_item = self.services_table.item(row, 1)
            price_item = self.services_table.item(row, 2)

            if not service_item or not qty_item or not price_item:
                continue

            try:
                service = service_item.text()
                qty = int(qty_item.text())
                price = float(price_item.text())
                line_total = qty * price
                total += line_total
                services.append((service, qty, price, line_total))
            except ValueError:
                continue

        if not services:
            QMessageBox.warning(self, "No Services", "Please add at least one valid service.")
            return

        services_text = " | ".join([f"{s} x{q} @₹{p:.2f}" for s, q, p, l in services])
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(self.get_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                services TEXT,
                total REAL,
                date TEXT,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            )
        """)
        cursor.execute("""
            INSERT INTO bills (patient_id, services, total, date)
            VALUES (?, ?, ?, ?)
        """, (self.patient_id, services_text, total, date))
        conn.commit()
        conn.close()

        self.total_label.setText(f"Total: ₹{total:.2f}")
        QMessageBox.information(self, "Success", "Bill generated successfully!")
        self.services_table.setRowCount(0)

        # Generate PDF
        self.generate_pdf_bill(services, total)

    def generate_pdf_bill(self, services, total):
        from PyQt5.QtCore import QDir

        logo_path = self.get_logo_path()
        patient_info = self.patient_details_label.text()
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        services_html = "".join([f"<tr><td>{s}</td><td>{q}</td><td>₹{p:.2f}</td><td>₹{l:.2f}</td></tr>" for s, q, p, l in services])

        html = f"""
        <html>
        <head><style>
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
        </style></head>
        <body>
            <img src="{logo_path}" height="80" />
            <h2>Hospital Bill</h2>
            <p><strong>Patient Info:</strong> {patient_info}</p>
            <p><strong>Date:</strong> {date}</p>
            <h3>Services</h3>
            <table>
                <tr><th>Service</th><th>Quantity</th><th>Price</th><th>Total</th></tr>
                {services_html}
            </table>
            <h3>Total Amount: ₹{total:.2f}</h3>
        </body>
        </html>
        """

        document = QTextDocument()
        document.setHtml(html)

        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        output_dir = os.path.join(os.path.expanduser("~"), "Documents")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        filename = f"Bill_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(output_dir, filename)
        printer.setOutputFileName(output_path)

        document.print_(printer)
        QMessageBox.information(self, "PDF Saved", f"Bill saved to {output_path}")
