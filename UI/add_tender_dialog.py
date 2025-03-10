import os
import pandas as pd
import uuid
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDateEdit, QPushButton, QComboBox, QMessageBox
from PySide6.QtCore import Qt
from UI import resource_path

class AddTenderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Tender")
        self.setFixedSize(400, 400)  # Made taller to accommodate new fields

        layout = QVBoxLayout()

        # Title Input
        self.title_label = QLabel("Tender Title:")
        self.title_input = QLineEdit()
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_input)

        # Link Input
        self.link_label = QLabel("Tender Link:")
        self.link_input = QLineEdit()
        layout.addWidget(self.link_label)
        layout.addWidget(self.link_input)

        # Category Input
        self.category_label = QLabel("Category:")
        self.category_input = QLineEdit()
        layout.addWidget(self.category_label)
        layout.addWidget(self.category_input)

        # Open/Amendment Date Picker (stored as date_posted)
        self.date_label = QLabel("Open/Amendment Date:")
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
        self.submit_button.clicked.connect(self.add_tender_to_csv)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def add_tender_to_csv(self):
        """
        Reads the input fields and appends a new row to the CSV file.
        Manually added tenders are given a unique hexadecimal ID to distinguish them
        from scraped tenders.
        """
        title = self.title_input.text()
        date_posted = self.date_picker.date().toString("yyyy-MM-dd")
        closing_date = self.close_date_picker.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentText()
        link = self.link_input.text()
        category = self.category_input.text()  # Get category from text input

        if title:
            file_path = resource_path("tender_data/filtered_tenders.csv")
            if not os.path.exists(file_path):
                QMessageBox.critical(self, "Error", "Could not find tender data file. Please ensure the application is properly set up.")
                return
            
            try:
                df = pd.read_csv(file_path)
                new_id = uuid.uuid4().hex
                new_row = pd.DataFrame([{
                    "id": new_id,
                    "title": title,
                    "date_posted": date_posted,
                    "closing_date": closing_date,
                    "link": link,
                    "category": category,
                    "status": status
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(file_path, index=False)
                self.accept()  # Close dialog on success
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save tender: {str(e)}")
        else:
            QMessageBox.warning(self, "Validation Error", "Title is required.")
