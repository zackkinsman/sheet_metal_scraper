import sys
import os
import shutil
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView, QDialog
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtCore import Qt, QStandardPaths
from UI.tender_ui import Ui_MainWindow 
from UI.add_tender_dialog import AddTenderDialog 

def get_db_path():
    """
    Locate the bundled tenders.db (assumed to be in the db folder relative to the project root),
    and copy it to a writable location (AppDataLocation) if it doesn't already exist.
    """
    # Determine the base path for the bundled file.
    if getattr(sys, 'frozen', False):
        # When frozen, files are in sys._MEIPASS.
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    
    # Construct the absolute path to the bundled database.
    # Assuming the bundled database is located in the db folder at the project root.
    bundled_db_path = os.path.abspath(os.path.join(base_path, "db", "tenders.db"))
    
    # Determine a writable location for the database.
    writable_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    if not os.path.exists(writable_dir):
        os.makedirs(writable_dir)
    writable_db_path = os.path.join(writable_dir, "tenders.db")
    
    # If the writable copy doesn't exist, copy the bundled database there.
    if not os.path.exists(writable_db_path):
        try:
            shutil.copy(bundled_db_path, writable_db_path)
            print("Database copied to writable location:", writable_db_path)
        except Exception as e:
            print("Error copying database:", e)
    else:
        print("Writable database already exists:", writable_db_path)
    
    return writable_db_path

class TenderBackend(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Setup Database Connection
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        # Use the get_db_path() function to get the correct, writable database path.
        db_path = get_db_path()
        self.db.setDatabaseName(db_path)
        if not self.db.open():
            print("Error: Unable to open database")
            sys.exit(1)

        # Setup Table Model for Direct DB Access
        self.model = QSqlTableModel(self, self.db)
        self.model.setTable("tenders")
        self.model.select()
        # New schema: id, title, description, date_posted, open_date, closing_date, link, status
        self.model.setHeaderData(1, Qt.Horizontal, "Title")
        self.model.setHeaderData(3, Qt.Horizontal, "Date Posted")
        self.model.setHeaderData(4, Qt.Horizontal, "Open Date")
        self.model.setHeaderData(5, Qt.Horizontal, "Closing Date")
        self.model.setHeaderData(7, Qt.Horizontal, "Status")

        # Use the existing QTableView from the UI (named TenderList)
        self.ui.TenderList.setModel(self.model)
        self.ui.TenderList.setSelectionBehavior(QTableView.SelectRows)
        self.ui.TenderList.setSelectionMode(QTableView.SingleSelection)
        # Hide columns not required for display: id (0), description (2), link (6)
        self.ui.TenderList.setColumnHidden(0, True)
        self.ui.TenderList.setColumnHidden(2, True)
        self.ui.TenderList.setColumnHidden(6, True)

        # Connect UI Buttons
        self.ui.MarkAsInterestedButton.clicked.connect(self.mark_selected_tender)
        self.ui.ExportToPDFButton.clicked.connect(lambda: print("Export to PDF functionality to be implemented."))
        self.ui.AddTenderButton.clicked.connect(self.open_add_tender_dialog)

    def mark_selected_tender(self):
        """
        Mark the selected tender as Interested in the database.
        """
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
            self.model.select()  # Refresh the table to show the new tender

def run_ui():
    app = QApplication(sys.argv)
    main_window = TenderBackend()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_ui()
