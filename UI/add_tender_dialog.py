# add_tender_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDateEdit, QPushButton, QComboBox
from PySide6.QtCore import Qt
import sqlite3

class AddTenderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Tender")
        self.setFixedSize(400, 300)  # Set a fixed size for the modal

        # Layout
        layout = QVBoxLayout()

        # Title Input
        self.title_label = QLabel("Tender Title:")
        self.title_input = QLineEdit()
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_input)

        # Description Input
        self.desc_label = QLabel("Description:")
        self.desc_input = QLineEdit()
        layout.addWidget(self.desc_label)
        layout.addWidget(self.desc_input)

        # Date Posted Picker
        self.date_label = QLabel("Date Posted:")
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        layout.addWidget(self.date_label)
        layout.addWidget(self.date_picker)

        # Closing Date Picker
        self.close_date_label = QLabel("Closing Date:")
        self.close_date_picker = QDateEdit()
        self.close_date_picker.setCalendarPopup(True)
        layout.addWidget(self.close_date_label)
        layout.addWidget(self.close_date_picker)

        # Status Dropdown
        self.status_label = QLabel("Status:")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Open", "Closed", "Interested", "Under Review"])
        layout.addWidget(self.status_label)
        layout.addWidget(self.status_combo)

        # Submit Button
        self.submit_button = QPushButton("Add Tender")
        self.submit_button.clicked.connect(self.add_tender_to_db)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def add_tender_to_db(self):
        """Insert the new tender into the database."""
        title = self.title_input.text()
        description = self.desc_input.text()
        date_posted = self.date_picker.date().toString("yyyy-MM-dd")
        closing_date = self.close_date_picker.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentText()

        if title and description:
            conn = sqlite3.connect("tenders.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tenders (title, description, date_posted, open_date, closing_date, link, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, description, date_posted, "", closing_date, "", status))
            conn.commit()
            conn.close()

            self.accept()  # Close dialog after successful insertion
        else:
            print("Title and description are required.")
