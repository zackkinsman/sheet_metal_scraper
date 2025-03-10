import sys
import os
import pandas as pd
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView, QDialog, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from UI.tender_ui import Ui_MainWindow 
from UI.add_tender_dialog import AddTenderDialog
from UI import resource_path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class TenderBackend(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # CSV file path (stored in the tender_data folder)
        self.csv_file = resource_path("tender_data/filtered_tenders.csv")
        
        if not os.path.exists(self.csv_file):
            QMessageBox.critical(self, "Error", "Could not find tender data file. Please ensure the application data files are properly set up.")
            sys.exit(1)
            
        # Load CSV data into a QStandardItemModel
        try:
            self.model = self.load_csv_model()
            self.ui.TenderList.setModel(self.model)
            self.ui.TenderList.setSelectionBehavior(QTableView.SelectRows)
            self.ui.TenderList.setSelectionMode(QTableView.SingleSelection)
            # Ensure title column is visible and first
            self.ui.TenderList.setColumnHidden(0, False)
            self.ui.TenderList.horizontalHeader().moveSection(0, 0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tender data: {str(e)}")
            sys.exit(1)

        # Connect UI Buttons
        self.ui.ExportToPDFButton.clicked.connect(self.export_to_pdf)
        self.ui.AddTenderButton.clicked.connect(self.open_add_tender_dialog)
        self.ui.ScrapeTendersButton.clicked.connect(self.scrape_tenders)
        self.ui.TenderList.selectionModel().selectionChanged.connect(self.display_tender_details)
        
        self.show()

    def load_csv_model(self):
        """
        Loads the CSV file into a QStandardItemModel.
        """
        df = pd.read_csv(self.csv_file)
        model = QStandardItemModel()
        headers = ['title', 'link', 'category', 'date_posted', 'closing_date', 'organization']
        model.setColumnCount(len(headers))
        model.setHorizontalHeaderLabels(headers)
        for _, row in df.iterrows():
            items = [QStandardItem(str(row[col])) for col in headers]
            model.appendRow(items)
        self.df = df  # Store the dataframe for later use
        return model

    def display_tender_details(self, selected, deselected):
        """
        Displays the details of the selected tender in the TenderDetails section.
        """
        if selected.indexes():
            index = selected.indexes()[0].row()
            tender = self.df.iloc[index]
            self.ui.TenderDetails.setTitle(tender['title'])  # Set the group box title
            self.ui.TenderName.setText(tender['title'])
            self.ui.TenderExpandedInfo.setText(tender['Full Description'])

    def save_model_to_csv(self):
        """
        Saves the current data from the QStandardItemModel back to the CSV file.
        """
        rows = self.model.rowCount()
        cols = self.model.columnCount()
        headers = [self.model.headerData(col, Qt.Horizontal) for col in range(cols)]
        data = []
        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = self.model.item(row, col)
                row_data.append(item.text() if item is not None else "")
            data.append(row_data)
        df = pd.DataFrame(data, columns=headers)
        df.to_csv(self.csv_file, index=False)

    def export_to_pdf(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_path:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            
            # PDF formatting settings
            margin_left = 50
            margin_top = 50
            max_width = 500  # Maximum width for text
            line_height = 15
            y = height - margin_top
            
            # Add title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(margin_left, y, "Tender List")
            y -= line_height * 2
            
            # Add headers
            c.setFont("Helvetica-Bold", 12)
            headers = [self.model.headerData(col, Qt.Horizontal) for col in range(self.model.columnCount())]
            
            # Process each row
            c.setFont("Helvetica", 10)
            for row in range(self.model.rowCount()):
                # Check if we need a new page
                if y < 50:  # Leave margin at bottom
                    c.showPage()
                    y = height - margin_top
                    c.setFont("Helvetica", 10)
                
                # Get tender data
                tender_title = self.model.item(row, 0).text()
                tender_link = self.model.item(row, 1).text()
                tender_category = self.model.item(row, 2).text()
                date_posted = self.model.item(row, 3).text()
                closing_date = self.model.item(row, 4).text()
                organization = self.model.item(row, 5).text()
                
                # Draw tender information with proper formatting
                c.setFont("Helvetica-Bold", 11)
                y -= line_height
                c.drawString(margin_left, y, f"{tender_title}")
                
                c.setFont("Helvetica", 10)
                y -= line_height
                c.drawString(margin_left, y, f"Organization: {organization}")
                y -= line_height
                c.drawString(margin_left, y, f"Category: {tender_category}")
                y -= line_height
                c.drawString(margin_left, y, f"Posted: {date_posted}  |  Closes: {closing_date}")
                y -= line_height
                c.drawString(margin_left, y, f"Link: {tender_link}")
                
                # Add spacing between entries
                y -= line_height * 1.5
            
            c.save()

    def open_add_tender_dialog(self):
        """
        Opens the Add Tender dialog. On success, reloads the CSV model and refreshes the UI.
        """
        dialog = AddTenderDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # After adding a tender, reload the model.
            self.model = self.load_csv_model()
            self.ui.TenderList.setModel(self.model)

    def scrape_tenders(self):
        """
        Calls the scraper script to scrape tenders and update the CSV file.
        """
        try:
            if not os.path.exists(resource_path("scraper/scraper.py")) or \
               not os.path.exists(resource_path("scraper/scraper_links.py")) or \
               not os.path.exists(resource_path("scraper/deepseek_filter.py")):
                QMessageBox.critical(self, "Error", "Scraper scripts not found. Please ensure the application is properly set up.")
                return
                
            subprocess.run(["python", resource_path("scraper/scraper.py")], check=True)
            subprocess.run(["python", resource_path("scraper/scraper_links.py")], check=True)
            subprocess.run(["python", resource_path("scraper/deepseek_filter.py")], check=True)
            # Reload the model after scraping
            self.model = self.load_csv_model()
            self.ui.TenderList.setModel(self.model)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Error occurred while scraping tenders: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error while scraping: {str(e)}")

def run_ui():
    app = QApplication(sys.argv)
    main_window = TenderBackend()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_ui()
