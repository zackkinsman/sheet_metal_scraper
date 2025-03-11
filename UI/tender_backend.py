import sys
import os
import pandas as pd
import subprocess
import threading
import traceback
import time
import importlib.util
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView, QDialog, QFileDialog, QMessageBox, QProgressDialog
from PySide6.QtCore import Qt, QTimer, Signal, QObject
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
        Calls the scraper script to scrape tenders and update the CSV file in a background thread.
        Shows a progress dialog while scraping is in progress.
        """
        # Create log file in the project root directory for easy access
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        log_file = os.path.join(desktop_path, "scraper_error.log")
        
        try:
            # Make sure we can write to the log file
            with open(log_file, "w") as f:
                f.write(f"=== Scraper Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            
            # Debug information to locate the scripts
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            script_paths = {
                'scraper.py': resource_path("scraper/scraper.py"),
                'scraper_links.py': resource_path("scraper/scraper_links.py"),
                'deepseek_filter.py': resource_path("scraper/deepseek_filter.py")
            }
            
            # Direct script paths (fallback option)
            direct_paths = {
                'scraper.py': os.path.join(base_dir, "scraper", "scraper.py"),
                'scraper_links.py': os.path.join(base_dir, "scraper", "scraper_links.py"),
                'deepseek_filter.py': os.path.join(base_dir, "scraper", "deepseek_filter.py")
            }
            
            # Log path information
            with open(log_file, "a") as f:
                f.write("\n=== Path Resolution ===\n")
                for name, path in script_paths.items():
                    exists = os.path.exists(path)
                    f.write(f"  {name}: {path} - Exists: {exists}\n")
                
            # Use either resource_path resolution or direct paths, whichever works
            scripts_to_use = {}
            missing_scripts = []
            
            for name, path in script_paths.items():
                if os.path.exists(path):
                    scripts_to_use[name] = path
                elif os.path.exists(direct_paths[name]):
                    scripts_to_use[name] = direct_paths[name]
                else:
                    missing_scripts.append(f"{name}")
            
            if missing_scripts:
                error_msg = f"The following scraper scripts were not found: {', '.join(missing_scripts)}"
                QMessageBox.critical(self, "Error", error_msg)
                return
            
            # Create a progress dialog with cancel button
            progress = QProgressDialog("Initializing scraper...", "Cancel", 0, 100, self)
            progress.setWindowTitle("Scraping Tenders")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            progress.show()
            
            # Add a countdown timer to show in progress dialog
            self.progress_text = "Initializing..."
            self.timeout_counter = 0
            self.update_timer = QTimer(self)
            self.update_timer.timeout.connect(lambda: self.update_progress_dialog(progress))
            self.update_timer.start(1000)  # Update every 1 second
            
            # Connect cancel button to termination function
            progress.canceled.connect(self.cancel_scraping)
            
        except Exception as e:
            error_msg = f"Unexpected error while setting up scraping: {str(e)}"
            with open(log_file, "a") as f:
                f.write(f"\n=== UNEXPECTED ERROR ===\n")
                f.write(f"{error_msg}\n")
                f.write(traceback.format_exc())
            
            QMessageBox.critical(self, "Error", f"{error_msg}")
    
    def update_progress_message(self, message):
        """Update the progress message text"""
        self.progress_text = message
        self.timeout_counter = 0  # Reset timeout counter when progress occurs
    
    def update_progress_dialog(self, progress_dialog):
        """Update the progress dialog with timing information"""
        self.timeout_counter += 1
        
        # Calculate minutes and seconds
        minutes = self.timeout_counter // 60
        seconds = self.timeout_counter % 60
        
        # Show timeout information along with progress message
        time_text = f"{minutes:02d}:{seconds:02d}"
        progress_dialog.setLabelText(f"{self.progress_text}\n\nRunning for: {time_text}")
        
        # If we've been running for more than 5 minutes, show warning
        if self.timeout_counter >= 300:  # 5 minutes
            progress_dialog.setValue(99)  # Almost done
            if self.timeout_counter % 60 == 0:  # Once a minute
                with open(os.path.join(os.path.expanduser("~"), "Desktop", "scraper_error.log"), "a") as f:
                    f.write(f"\n=== WARNING: Scraping has been running for {minutes} minutes ===\n")
                    f.write("Script may be stuck. Consider cancelling the operation.\n")
    
    def cancel_scraping(self):
        """Handle cancellation of the scraping process"""
        self.update_timer.stop()
        
        # Log the cancellation
        with open(os.path.join(os.path.expanduser("~"), "Desktop", "scraper_error.log"), "a") as f:
            f.write(f"\n=== SCRAPING CANCELLED BY USER after {self.timeout_counter} seconds ===\n")
    
    def scraping_finished(self, success, error_message, progress_dialog):
        """Handle completion of the scraping process."""
        # Stop the update timer
        self.update_timer.stop()
        
        # Close the progress dialog
        progress_dialog.close()
        
        if success:
            # Reload the model after scraping
            try:
                self.model = self.load_csv_model()
                self.ui.TenderList.setModel(self.model)
                QMessageBox.information(self, "Success", "Tenders have been scraped and updated successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error reloading tender data: {str(e)}")
        else:
            log_path = os.path.join(os.path.expanduser("~"), "Desktop", "scraper_error.log")
            QMessageBox.critical(self, "Error", 
                                f"Error occurred while scraping tenders:\n{error_message}\n\n"
                                f"See the log file for details:\n{log_path}")

def run_ui():
    app = QApplication(sys.argv)
    main_window = TenderBackend()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_ui()
