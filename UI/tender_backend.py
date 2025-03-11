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
        # Resolve the ChromeDriver path and set it as an environment variable for the scraper
        chrome_driver_path = resource_path("chromedriver-win64/chromedriver.exe")
        os.environ["CHROMEDRIVER_PATH"] = chrome_driver_path

        # Create log file on Desktop for easy access
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        log_file = os.path.join(desktop_path, "scraper_error.log")
        try:
            with open(log_file, "w") as f:
                f.write(f"=== Scraper Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot write to log file: {str(e)}")
            return

        # (Optional) Log the ChromeDriver path for debugging
        with open(log_file, "a") as f:
            f.write(f"\nChromeDriver Path: {chrome_driver_path}\n")
        
        # Resolve paths for your scraper scripts as before
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_paths = {
            'scraper.py': resource_path("scraper/scraper.py"),
            'scraper_links.py': resource_path("scraper/scraper_links.py"),
            'deepseek_filter.py': resource_path("scraper/deepseek_filter.py")
        }
        direct_paths = {
            'scraper.py': os.path.join(base_dir, "scraper", "scraper.py"),
            'scraper_links.py': os.path.join(base_dir, "scraper", "scraper_links.py"),
            'deepseek_filter.py': os.path.join(base_dir, "scraper", "deepseek_filter.py")
        }
        
        with open(log_file, "a") as f:
            f.write("\n=== Path Resolution ===\n")
            for name, path in script_paths.items():
                exists = os.path.exists(path)
                f.write(f"  {name}: {path} - Exists: {exists}\n")
        
        scripts_to_use = {}
        missing_scripts = []
        for name, path in script_paths.items():
            if os.path.exists(path):
                scripts_to_use[name] = path
            elif os.path.exists(direct_paths[name]):
                scripts_to_use[name] = direct_paths[name]
            else:
                missing_scripts.append(name)
        
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
        
        # Start a timer to update the progress dialog
        self.progress_text = "Initializing..."
        self.timeout_counter = 0
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(lambda: self.update_progress_dialog(progress))
        self.update_timer.start(1000)  # Update every second
        
        progress.canceled.connect(self.cancel_scraping)
        
        # Start the scraping process in a background thread
        thread = threading.Thread(target=self.run_scraper, args=(scripts_to_use, progress, log_file))
        thread.start()

    def run_scraper(self, scripts_to_use, progress_dialog, log_file):
        import subprocess, sys, os
        try:
            # Set up environment variables for resource paths
            env = os.environ.copy()
            env["TENDER_DATA_PATH"] = resource_path("tender_data")
            env["LAST_ID_PATH"] = resource_path("last_id.txt")
            env["KEYWORDS_PATH"] = resource_path("tender_data/Tender_Keywords.csv")
            env["NO_UI"] = "1"  # Prevent UI initialization in subprocess
            
            # Run scripts in sequence
            script_sequence = ['scraper.py', 'scraper_links.py', 'deepseek_filter.py']
            success = True
            error_message = ""
            
            for script_name in script_sequence:
                self.progress_text = f"Running {script_name}..."
                result = subprocess.run(
                    [sys.executable, scripts_to_use[script_name]],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
                )
                
                # Log stdout and stderr for debugging
                with open(log_file, "a") as f:
                    f.write(f"\n=== {script_name} STDOUT ===\n{result.stdout}\n")
                    f.write(f"\n=== {script_name} STDERR ===\n{result.stderr}\n")
                
                if result.returncode != 0:
                    error_message = f"{script_name} failed with exit status {result.returncode}"
                    success = False
                    break
            
        except Exception as e:
            success = False
            error_message = str(e)
            with open(log_file, "a") as f:
                f.write(f"\nException while running scraper: {error_message}\n")
        
        # Finish progress on the main thread
        QTimer.singleShot(0, lambda: self.scraping_finished(success, error_message, progress_dialog))

    def update_progress_dialog(self, progress_dialog):
        """
        Updates the progress dialog with elapsed time information.
        """
        self.timeout_counter += 1
        minutes = self.timeout_counter // 60
        seconds = self.timeout_counter % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        progress_dialog.setLabelText(f"{self.progress_text}\n\nRunning for: {time_text}")
        if self.timeout_counter >= 300:
            progress_dialog.setValue(99)
            if self.timeout_counter % 60 == 0:
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                log_file = os.path.join(desktop_path, "scraper_error.log")
                with open(log_file, "a") as f:
                    f.write(f"\n=== WARNING: Scraping has been running for {minutes} minutes ===\n")

    def cancel_scraping(self):
        """
        Handles user cancellation of the scraping process.
        """
        self.update_timer.stop()
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        log_file = os.path.join(desktop_path, "scraper_error.log")
        with open(log_file, "a") as f:
            f.write(f"\n=== SCRAPING CANCELLED BY USER after {self.timeout_counter} seconds ===\n")

    def scraping_finished(self, success, error_message, progress_dialog):
        """
        Handle completion of the scraping process.
        """
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
