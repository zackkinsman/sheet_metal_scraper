import sys
import os
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from UI.tender_ui import Ui_MainWindow 
from UI.add_tender_dialog import AddTenderDialog

class TenderBackend(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # CSV file path (stored in the project root)
        self.csv_file = "filtered_tenders.csv"
        # Load CSV data into a QStandardItemModel
        self.model = self.load_csv_model()
        self.ui.TenderList.setModel(self.model)
        self.ui.TenderList.setSelectionBehavior(QTableView.SelectRows)
        self.ui.TenderList.setSelectionMode(QTableView.SingleSelection)
        # Hide the ID column (assumed to be column index 0)
        self.ui.TenderList.setColumnHidden(0, True)

        # Connect UI Buttons
        # The ExportToPDFButton functionality is a placeholder for now.
        self.ui.ExportToPDFButton.clicked.connect(self.export_to_pdf)
        self.ui.AddTenderButton.clicked.connect(self.open_add_tender_dialog)

    def load_csv_model(self):
        """
        Loads the CSV file into a QStandardItemModel.
        If the CSV doesn't exist, it creates an empty CSV with the proper headers.
        """
        # If the file doesn't exist, create it with proper headers.
        if not os.path.exists(self.csv_file):
            df = pd.DataFrame(columns=["id", "title", "description", "date_posted", "closing_date", "link", "status"])
            df.to_csv(self.csv_file, index=False)
        else:
            df = pd.read_csv(self.csv_file)
        
        model = QStandardItemModel()
        headers = list(df.columns)
        model.setColumnCount(len(headers))
        model.setHorizontalHeaderLabels(headers)
        for _, row in df.iterrows():
            items = [QStandardItem(str(row[col])) for col in headers]
            model.appendRow(items)
        return model

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
        # Placeholder for Export to PDF functionality
        print("Export to PDF functionality to be implemented.")

    def open_add_tender_dialog(self):
        """
        Opens the Add Tender dialog. On success, reloads the CSV model and refreshes the UI.
        """
        dialog = AddTenderDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # After adding a tender, reload the model.
            self.model = self.load_csv_model()
            self.ui.TenderList.setModel(self.model)

def run_ui():
    app = QApplication(sys.argv)
    main_window = TenderBackend()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_ui()
