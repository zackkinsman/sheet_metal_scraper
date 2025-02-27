import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PySide6.QtCore import Qt
from tender_ui import Ui_MainWindow
from database import create_tables, create_connection

class TenderBackend:
    def __init__(self):
        # Ensure the database and table exist
        create_tables()
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def load_tenders(self):
        """
        Retrieve tenders from the database.
        Returns a list of tuples: (id, title, date_posted, closing_date, status)
        """
        self.cursor.execute("SELECT id, title, date_posted, closing_date, status FROM tenders")
        return self.cursor.fetchall()

    def get_tender_details(self, tender_id):
        """
        Retrieve full details of a tender given its ID.
        Returns a dictionary with keys: id, title, description, date_posted, open_date, closing_date, link, status.
        """
        self.cursor.execute(
            "SELECT id, title, description, date_posted, open_date, closing_date, link, status FROM tenders WHERE id = ?",
            (tender_id,)
        )
        row = self.cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "date_posted": row[3],
                "open_date": row[4],
                "closing_date": row[5],
                "link": row[6],
                "status": row[7]
            }
        return None

    def mark_as_interested(self, tender_id):
        """
        Mark a tender as interested by updating its status.
        """
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
        """
        Load tenders from the DB and display them in the table.
        The tender id is stored in the first column item's Qt.UserRole for later use.
        """
        tenders = backend.load_tenders()
        ui.TendeList.setRowCount(len(tenders))
        for row_index, tender in enumerate(tenders):
            # Create item for title and store the tender id in Qt.UserRole.
            title_item = QTableWidgetItem(tender[1])
            title_item.setData(Qt.UserRole, tender[0])
            ui.TendeList.setItem(row_index, 0, title_item)
            
            # Display Date Posted, Closing Date, and Status in the subsequent columns.
            ui.TendeList.setItem(row_index, 1, QTableWidgetItem(str(tender[2])))
            ui.TendeList.setItem(row_index, 2, QTableWidgetItem(str(tender[3])))
            ui.TendeList.setItem(row_index, 3, QTableWidgetItem(str(tender[4])))

    def mark_selected_tender():
        """
        Mark the selected tender as Interested.
        Retrieves the tender id from the hidden data in the first column.
        """
        selected_items = ui.TendeList.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            # Retrieve the tender id stored in the first column's item.
            tender_id = ui.TendeList.item(row, 0).data(Qt.UserRole)
            tender_title = ui.TendeList.item(row, 0).text()
            print(f"Marking tender '{tender_title}' (ID: {tender_id}) as Interested.")
            backend.mark_as_interested(tender_id)
            refresh_tender_list()
        else:
            print("No tender selected.")

    # --- Connect UI Buttons ---
    ui.ScrapeTendersButton.clicked.connect(lambda: print("Scrape Tenders functionality to be implemented."))
    ui.MarkAsInterestedButton.clicked.connect(mark_selected_tender)
    ui.ExportToPDFButton.clicked.connect(lambda: print("Export to PDF functionality to be implemented."))

    # Initially load and display tenders
    refresh_tender_list()

    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_ui()
