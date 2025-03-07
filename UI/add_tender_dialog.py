import os
import pandas as pd
import uuid
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDateEdit, QPushButton, QComboBox
from PySide6.QtCore import Qt

class AddTenderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Tender")
        self.setFixedSize(400, 300)

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
        description = self.desc_input.text()
        date_posted = self.date_picker.date().toString("yyyy-MM-dd")
        closing_date = self.close_date_picker.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentText()

        if title and description:
            file_path = "filtered_tenders.csv"
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
            else:
                df = pd.DataFrame(columns=["id", "title", "description", "date_posted", "closing_date", "link", "status"])
            
            # Generate a unique hex ID for the manually added tender
            new_id = uuid.uuid4().hex

            new_row = {
                "id": new_id,
                "title": title,
                "description": description,
                "date_posted": date_posted,
                "closing_date": closing_date,
                "link": "",
                "status": status
            }
            # Append the new row and save back to CSV
            df = df.append(new_row, ignore_index=True)
            df.to_csv(file_path, index=False)
            self.accept()  # Close dialog on success
        else:
            print("Title and description are required.")
