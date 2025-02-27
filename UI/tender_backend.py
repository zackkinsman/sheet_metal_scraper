# tender_backend.py
import sys
import sqlite3
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from tender_ui import Ui_MainWindow
from database import create_tables, create_connection

class TenderBackend:
    def __init__(self):
        # Ensure the database and table exist
        create_tables()
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def load_tenders(self):
        """Retrieve tenders from the database.
           Returns a list of tuples (id, name, date_posted, closing_date, status)."""
        self.cursor.execute("SELECT id, name, date_posted, closing_date, status FROM tenders")
        return self.cursor.fetchall()

    def mark_as_interested(self, tender_id):
        """Mark a tender as interested (update its status)."""
        self.cursor.execute("UPDATE tenders SET status = ? WHERE id = ?", ("Interested", tender_id))
        self.conn.commit()

def run_ui():
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(main_window)

    backend = TenderBackend()

    # --- Helper Functions ---
    def refresh_tender_list():
        """Load tenders from the DB and display them in the table."""
        tenders = backend.load_tenders()
        # For simplicity, assume we display name, date_posted, closing_date, and status.
        ui.TendeList.setRowCount(len(tenders))
        for row_index, tender in enumerate(tenders):
            # tender[0] is id, so we start displaying from tender[1]
            for col_index, value in enumerate(tender[1:]):
                ui.TendeList.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    def mark_selected_tender():
        """Stub for marking the selected tender as 'Interested'."""
        selected_items = ui.TendeList.selectedItems()
        if selected_items:
            # Assume the table is set up so that the first (hidden) column is the DB id.
            # Here, we use the first displayed column (name) for demonstration.
            row = selected_items[0].row()
            # In a real implementation, you might store the tender id in a hidden column.
            # For now, we simulate by printing the tender name.
            tender_name = ui.TendeList.item(row, 0).text()
            print(f"Marking tender '{tender_name}' as Interested.")
            # backend.mark_as_interested(tender_id) would be called if you had the id.
            # Then refresh the list to show updated status.
            refresh_tender_list()
        else:
            print("No tender selected.")

    # --- Connect UI Buttons ---
    ui.ScrapeTendersButton.clicked.connect(lambda: print("Scrape Tenders functionality to be implemented."))
    ui.MarkAsInterestedButton.clicked.connect(mark_selected_tender)
    ui.ExportToPDFButton.clicked.connect(lambda: print("Export to PDF functionality to be implemented."))

    # Initially load and display tenders (you can also add dummy data to the DB for testing)
    refresh_tender_list()

    main_window.show()
    sys.exit(app.exec())
