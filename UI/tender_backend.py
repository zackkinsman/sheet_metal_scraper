import sys
import os
from urllib.parse import urlparse
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView, QDialog
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtCore import Qt
from UI.tender_ui import Ui_MainWindow 
from UI.add_tender_dialog import AddTenderDialog 
from dotenv import load_dotenv

load_dotenv()

class TenderBackend(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Setup PostgreSQL Database Connection using the QPSQL driver
        self.db = QSqlDatabase.addDatabase("QPSQL")
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            result = urlparse(database_url)
            self.db.setHostName(result.hostname)
            self.db.setPort(result.port)
            self.db.setDatabaseName(result.path.lstrip("/"))
            self.db.setUserName(result.username)
            self.db.setPassword(result.password)
        if not self.db.open():
            print("Error: Unable to open database")
            sys.exit(1)

        # Setup Table Model for Direct DB Access (table: id, title, description, date_posted, closing_date, link, status)
        self.model = QSqlTableModel(self, self.db)
        self.model.setTable("tenders")
        self.model.select()
        self.model.setHeaderData(1, Qt.Horizontal, "Title")
        self.model.setHeaderData(2, Qt.Horizontal, "Description")
        self.model.setHeaderData(3, Qt.Horizontal, "Open/Amendment Date")
        self.model.setHeaderData(4, Qt.Horizontal, "Closing Date")
        self.model.setHeaderData(5, Qt.Horizontal, "Link")
        self.model.setHeaderData(6, Qt.Horizontal, "Status")

        self.ui.TenderList.setModel(self.model)
        self.ui.TenderList.setSelectionBehavior(QTableView.SelectRows)
        self.ui.TenderList.setSelectionMode(QTableView.SingleSelection)
        self.ui.TenderList.setColumnHidden(0, True)  # Hide the ID column

        # Connect UI Buttons
        self.ui.MarkAsInterestedButton.clicked.connect(self.mark_selected_tender)
        self.ui.ExportToPDFButton.clicked.connect(lambda: print("Export to PDF functionality to be implemented."))
        self.ui.AddTenderButton.clicked.connect(self.open_add_tender_dialog)

    def mark_selected_tender(self):
        selected_rows = self.ui.TenderList.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            tender_id = self.model.record(row).value("id")

            record = self.model.record(row)
            record.setValue("status", "Interested")
            self.model.setRecord(row, record)
            self.model.submitAll()

            print(f"Marked Tender ID {tender_id} as 'Interested'.")
        else:
            print("No tender selected.")

    def open_add_tender_dialog(self):
        dialog = AddTenderDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.model.select()  # Refresh the table

def run_ui():
    app = QApplication(sys.argv)
    main_window = TenderBackend()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_ui()
