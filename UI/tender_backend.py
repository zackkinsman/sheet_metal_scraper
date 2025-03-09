import sys
import os
import pandas as pd
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView, QDialog, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from UI.tender_ui import Ui_MainWindow 
from UI.add_tender_dialog import AddTenderDialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class TenderBackend(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # CSV file path (stored in the tender_data folder)
        self.csv_file = "tender_data/filtered_tenders.csv"
        # Load CSV data into a QStandardItemModel
        self.model = self.load_csv_model()
        self.ui.TenderList.setModel(self.model)
        self.ui.TenderList.setSelectionBehavior(QTableView.SelectRows)
        self.ui.TenderList.setSelectionMode(QTableView.SingleSelection)
        # Hide the ID column (assumed to be column index 0)
        self.ui.TenderList.setColumnHidden(0, True)

        # Connect UI Buttons
        self.ui.ExportToPDFButton.clicked.connect(self.export_to_pdf)
        self.ui.AddTenderButton.clicked.connect(self.open_add_tender_dialog)
        self.ui.ScrapeTendersButton.clicked.connect(self.scrape_tenders)
        self.ui.TenderList.selectionModel().selectionChanged.connect(self.display_tender_details)

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
            c.drawString(100, height - 100, "Tender List")
            y = height - 150
            for row in range(self.model.rowCount()):
                text = " | ".join([self.model.item(row, col).text() for col in range(self.model.columnCount())])
                c.drawString(100, y, text)
                y -= 20
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
            subprocess.run(["python", "scraper/scraper.py"], check=True)
            subprocess.run(["python", "scraper/scraper_links.py"], check=True)
            # Reload the model after scraping
            self.model = self.load_csv_model()
            self.ui.TenderList.setModel(self.model)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while scraping tenders: {e}")

def run_ui():
    app = QApplication(sys.argv)
    main_window = TenderBackend()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_ui()
