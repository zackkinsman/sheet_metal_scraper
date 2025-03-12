import sys
import os
import pandas as pd
import subprocess
import threading
import requests
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableView, QDialog, 
                              QFileDialog, QMessageBox, QProgressDialog, QListWidgetItem,
                              QVBoxLayout, QLabel, QAbstractItemView)
from PySide6.QtCore import Qt, QTimer, QMimeData, QUrl, Signal, QObject
from PySide6.QtGui import QStandardItemModel, QStandardItem, QDragEnterEvent, QDropEvent
from UI.tender_ui import Ui_MainWindow 
from UI.add_tender_dialog import AddTenderDialog
from UI import resource_path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Supported file extensions and their handling methods
SUPPORTED_EXTENSIONS = {
    '.pdf': 'extract_text_from_pdf',
    '.docx': 'extract_text_from_docx',
    '.doc': 'extract_text_from_doc',
    '.txt': 'extract_text_from_txt',
    '.rtf': 'extract_text_from_rtf'
}

# Worker class to handle signals between threads
class WorkerSignals(QObject):
    update_progress = Signal(int)
    update_text = Signal(str)
    clear_text = Signal()
    finished = Signal()
    error = Signal(str)

class TenderBackend(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Initialize signals for cross-thread communication
        self.worker_signals = WorkerSignals()
        self.worker_signals.update_progress.connect(self.ui.ProcessProgress.setValue)
        self.worker_signals.update_text.connect(self.update_analysis_text)
        self.worker_signals.clear_text.connect(self.ui.AnalysisResults.clear)
        self.worker_signals.error.connect(self.show_error_message)
        
        # LM Studio API endpoint
        self.lm_studio_api = "http://localhost:1234/v1/chat/completions"
        
        # CSV file path (stored in the tender_data folder)
        self.csv_file = resource_path("tender_data/filtered_tenders.csv")
        
        # Initialize variables for file upload and processing
        self.uploaded_files = []
        
        # Set up the FileList QListWidget to allow multiple selection and checkable items
        self.ui.FileList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
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

        # Connect UI Buttons for tender page
        self.ui.ExportToPDFButton.clicked.connect(self.export_to_pdf)
        self.ui.AddTenderButton.clicked.connect(self.open_add_tender_dialog)
        self.ui.ScrapeTendersButton.clicked.connect(self.scrape_tenders)
        self.ui.TenderList.selectionModel().selectionChanged.connect(self.display_tender_details)
        
        # Connect navigation buttons
        self.ui.Tender_Button.clicked.connect(lambda: self.ui.PagePicker.setCurrentIndex(0))
        self.ui.AI_Analysis_Button.clicked.connect(lambda: self.ui.PagePicker.setCurrentIndex(1))
        self.ui.pushButton_3.clicked.connect(self.not_implemented_yet)
        
        # Connect AI Analysis page buttons
        self.ui.UploadFileButton.clicked.connect(self.upload_file)
        self.ui.ExportToPDFButton_2.clicked.connect(self.export_analysis_to_pdf)
        self.ui.ProcessTenderButton.clicked.connect(self.process_selected_documents)
        
        # Setup drag and drop for the AI Analysis page
        self.setup_drag_and_drop()
        
        # Initialize progress bar
        self.ui.ProcessProgress.setValue(0)
        
        # Start with tender page (page 0)
        self.ui.PagePicker.setCurrentIndex(0)
        
        self.show()
        
    def update_analysis_text(self, text):
        """Update the analysis text widget with the given text."""
        self.ui.AnalysisResults.setPlainText(text)
        
    def show_error_message(self, message):
        """Show an error message in the UI."""
        QMessageBox.critical(self, "Error", message)

    def setup_drag_and_drop(self):
        """Set up drag and drop functionality for the AI analysis page"""
        # Enable drag and drop for the DragAndDropFiles frame
        self.ui.DragAndDropFiles.setAcceptDrops(True)
        
        # Override the drag and drop event handlers
        self.ui.DragAndDropFiles.dragEnterEvent = self.drag_enter_event
        self.ui.DragAndDropFiles.dropEvent = self.drop_event
        
        # Add a label to indicate drag and drop area
        layout = self.ui.DragAndDropFiles.layout()
        if not layout:
            layout = QVBoxLayout(self.ui.DragAndDropFiles)
            self.ui.DragAndDropFiles.setLayout(layout)

            # Add a label to indicate drag and drop functionality
            drop_label = QLabel("Drag & Drop Files Here", self.ui.DragAndDropFiles)
            drop_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(drop_label)

    def drag_enter_event(self, event: QDragEnterEvent):
        """Handle drag enter events for file drops"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def drop_event(self, event: QDropEvent):
        """Handle drop events for files"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                # Check if it's a file and if it's a supported file type (PDF, DOCX, etc.)
                if os.path.isfile(file_path) and self.is_supported_file(file_path):
                    self.add_file_to_list(file_path)
            event.acceptProposedAction()
    
    def is_supported_file(self, file_path):
        """Check if the file type is supported"""
        _, ext = os.path.splitext(file_path)
        return ext.lower() in SUPPORTED_EXTENSIONS

    def add_file_to_list(self, file_path):
        """Add a file to the file list"""
        if file_path not in self.uploaded_files:
            self.uploaded_files.append(file_path)
            file_name = os.path.basename(file_path)
            
            # Create a new item for the list widget
            item = QListWidgetItem(file_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Make item checkable
            item.setCheckState(Qt.Checked)  # Default to checked
            item.setToolTip(file_path)  # Show full path on hover
            item.setData(Qt.UserRole, file_path)  # Store the file path in the item data
            
            # Add item to the list widget
            self.ui.FileList.addItem(item)
    
    def upload_file(self):
        """Open file dialog to select a file to upload"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Documents (*.pdf *.docx *.doc *.txt *.rtf)")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                self.add_file_to_list(file_path)
    
    def get_selected_files(self):
        """Get list of selected (checked) files from the list widget"""
        selected_files = []
        
        # Iterate through all items in the list widget
        for i in range(self.ui.FileList.count()):
            item = self.ui.FileList.item(i)
            if item.checkState() == Qt.Checked:
                file_path = item.data(Qt.UserRole)  # Get the file path from the item data
                selected_files.append(file_path)
        
        return selected_files
    
    def process_selected_documents(self):
        """Process only the selected documents"""
        selected_files = self.get_selected_files()
        
        if not selected_files:
            QMessageBox.warning(self, "No Files Selected", "Please select at least one document to process.")
            return
        
        # Reset progress bar and analysis results
        self.ui.ProcessProgress.setValue(0)
        self.ui.AnalysisResults.clear()
        
        # Show processing message
        self.ui.AnalysisResults.append(f"Processing {len(selected_files)} selected document(s). Please wait...")
        QApplication.processEvents()
        
        # Process documents in a background thread to avoid UI freezing
        thread = threading.Thread(target=self.process_documents_thread, args=(selected_files,))
        thread.daemon = True  # Make thread daemon so it exits when main thread exits
        thread.start()

    def process_documents_thread(self, files_to_process):
        """Process documents in a background thread"""
        try:
            # Analyze each document
            total_files = len(files_to_process)
            all_text_content = ""
            
            for i, file_path in enumerate(files_to_process):
                # Extract text from document
                file_ext = os.path.splitext(file_path)[1].lower()
                file_name = os.path.basename(file_path)
                
                # Update progress
                progress_value = int((i / total_files) * 50)  # First half of progress bar for extraction
                self.worker_signals.update_progress.emit(progress_value)
                
                try:
                    # Extract text based on file type
                    if file_ext == '.pdf':
                        text_content = self.extract_text_from_pdf(file_path)
                    elif file_ext in ('.docx', '.doc'):
                        text_content = self.extract_text_from_word(file_path)
                    elif file_ext == '.txt':
                        text_content = self.extract_text_from_txt(file_path)
                    elif file_ext == '.rtf':
                        text_content = self.extract_text_from_rtf(file_path)
                    else:
                        text_content = f"Unsupported file type: {file_ext}"
                    
                    # Add document content to combined text
                    all_text_content += f"\n--- Document: {file_name} ---\n{text_content}\n\n"
                    
                except Exception as e:
                    error_msg = f"Error extracting text from {file_name}: {str(e)}"
                    self.worker_signals.update_text.emit(error_msg)
                    return
            
            # Update progress to 50%
            self.worker_signals.update_progress.emit(50)
            
            if all_text_content:
                # Clear previous content
                self.worker_signals.clear_text.emit()
                
                # Show processing message
                self.worker_signals.update_text.emit("Sending to LM Studio for analysis...")
                
                # Send to LM Studio API
                analysis_result = self.analyze_with_lm_studio(all_text_content)
                
                # Log the result
                print(f"Analysis result received (first 100 chars): {analysis_result[:100] if analysis_result else 'None'}")
                
                # Update UI with results - THIS IS THE CRITICAL PART
                if analysis_result:
                    # Use the signal to update the UI from the background thread
                    self.worker_signals.clear_text.emit()  # Clear first
                    self.worker_signals.update_text.emit(analysis_result)
                else:
                    self.worker_signals.update_text.emit("No analysis was returned from LM Studio.")
            else:
                self.worker_signals.update_text.emit("No text content could be extracted from the selected documents.")
            
            # Update progress to 100%
            self.worker_signals.update_progress.emit(100)
            
        except Exception as e:
            # Display any errors that occurred during processing
            import traceback
            error_message = f"Error processing documents: {str(e)}\n{traceback.format_exc()}"
            print(f"Error in processing thread: {error_message}")
            self.worker_signals.error.emit(error_message)
            self.worker_signals.update_progress.emit(0)

    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            return "PyPDF2 library is not installed. Unable to extract text from PDF."
    
    def extract_text_from_word(self, file_path):
        """Extract text from Word document"""
        try:
            import docx
            doc = docx.Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except ImportError:
            return "python-docx library is not installed. Unable to extract text from Word document."
    
    def extract_text_from_txt(self, file_path):
        """Extract text from plain text file"""
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            return file.read()
    
    def extract_text_from_rtf(self, file_path):
        """Extract text from RTF file"""
        try:
            from striprtf.striprtf import rtf_to_text
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                rtf_text = file.read()
                text = rtf_to_text(rtf_text)
                return text
        except ImportError:
            return "striprtf library is not installed. Unable to extract text from RTF."
    
    def analyze_with_lm_studio(self, text_content):
        """Send document text to LM Studio API for analysis"""
        try:
            # Prepare the system prompt for document analysis
            system_prompt = """
            You are an expert tender document analyzer. Your task is to summarize the provided tender documents 
            and outline the key specifications and requirements. Extract as much relevant information as possible 
            and present it in a clear, organized format that is easily digestible. 
            
            Include:
            1. Project overview and scope
            2. Key requirements and specifications
            3. Submission deadlines and important dates
            4. Client/organization information
            5. Evaluation criteria if available
            6. Budget information if available
            7. Any unique or special requirements
            
            Format your response in a professional and structured manner with clear headings and bullet points 
            where appropriate.
            """
            
            # Prepare the API request payload using the qwen2.5-7b-instruct-1m model
            payload = {
                "model": "qwen2.5-7b-instruct-1m",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please analyze the following tender document(s): {text_content[:5000]}"}  # Limiting to 5000 chars for first part
                ],
                "temperature": 0.3,
                "max_tokens": -1,
                "stream": False
            }
            
            # If document is very large, add additional chunks as assistant responses
            text_chunks = [text_content[i:i+5000] for i in range(5000, len(text_content), 5000)]
            for chunk in text_chunks:
                payload["messages"].append({"role": "assistant", "content": "I'll continue analyzing the document."})
                payload["messages"].append({"role": "user", "content": chunk})
            
            # Make the API request
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.lm_studio_api, headers=headers, data=json.dumps(payload))
            
            # Check if the request was successful
            if response.status_code == 200:
                result = response.json()
                raw_analysis = result["choices"][0]["message"]["content"]
                # Clean the response to remove artifacts
                analysis = self.clean_ai_response(raw_analysis)
                return analysis
            else:
                return f"Error from LM Studio API: {response.status_code} - {response.text}"
        
        except Exception as e:
            return f"Error connecting to LM Studio API: {str(e)}\n\nPlease ensure LM Studio is running and the API server is accessible at {self.lm_studio_api}"
    
    def export_analysis_to_pdf(self):
        """Export the analysis results to a PDF file"""
        if not self.ui.AnalysisResults.toPlainText():
            QMessageBox.warning(self, "No Analysis", "There are no analysis results to export.")
            return
        
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Analysis PDF", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        
        if file_path:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            
            # PDF formatting settings
            margin_left = 50
            margin_top = 50
            line_height = 15
            y = height - margin_top
            
            # Add title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(margin_left, y, "Tender Document Analysis")
            y -= line_height * 2
            
            # Add analysis content
            c.setFont("Helvetica", 10)
            analysis_text = self.ui.AnalysisResults.toPlainText()
            lines = analysis_text.split("\n")
            
            for line in lines:
                # Check for heading lines to format them differently
                is_heading = False
                if line.strip() and all(c.isupper() for c in line if c.isalpha()):
                    is_heading = True
                    c.setFont("Helvetica-Bold", 12)
                
                if y < 50:  # Check if we need a new page
                    c.showPage()
                    y = height - margin_top
                    c.setFont("Helvetica", 10)
                
                # Handle long lines by wrapping text
                if len(line) > 95:  # Approximate number of chars that fit within margins
                    words = line.split()
                    current_line = ""
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        if len(test_line) <= 95:
                            current_line = test_line
                        else:
                            c.drawString(margin_left, y, current_line)
                            y -= line_height
                            current_line = word
                            
                            # Check page break again
                            if y < 50:
                                c.showPage()
                                y = height - margin_top
                                c.setFont("Helvetica-Bold", 12) if is_heading else c.setFont("Helvetica", 10)
                    
                    # Draw the last line if there's anything left
                    if current_line:
                        c.drawString(margin_left, y, current_line)
                        y -= line_height
                else:
                    c.drawString(margin_left, y, line)
                    y -= line_height
                
                # Reset font after drawing a heading
                if is_heading:
                    c.setFont("Helvetica", 10)
            
            c.save()
            QMessageBox.information(self, "Export Complete", "Analysis results have been exported to PDF.")

    def update_progress_dialog(self, progress_dialog):
        """
        Updates the progress dialog with elapsed time information.
        """
        self.timeout_counter += 1
        minutes = self.timeout_counter // 60
        seconds = self.timeout_counter % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        progress_dialog.setLabelText(f"{self.progress_text}\n\nRunning for: {time_text}")
        if self.timeout_counter >= 300:  # 5 minutes
            progress_dialog.setValue(99)

    def cancel_scraping(self):
        """
        Handles user cancellation of the scraping process.
        """
        self.update_timer.stop()
        self.scraping_cancelled = True

    def not_implemented_yet(self):
        """
        Display a message for functionality that's not yet implemented
        """
        QMessageBox.information(self, "Not Implemented", "This functionality is not yet implemented.")

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
        # Get absolute paths to eliminate path resolution issues
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Directly use absolute paths for ChromeDriver and scraper scripts
        chrome_driver_path = os.path.join(base_dir, "chromedriver-win64", "chromedriver.exe")
        if not os.path.exists(chrome_driver_path):
            chrome_driver_path = resource_path("chromedriver-win64/chromedriver.exe")
        
        os.environ["CHROMEDRIVER_PATH"] = chrome_driver_path
        
        # Use direct paths for the scripts since resource_path might be failing
        direct_paths = {
            'scraper.py': os.path.join(base_dir, "scraper", "scraper.py"),
            'scraper_links.py': os.path.join(base_dir, "scraper", "scraper_links.py"),
            'deepseek_filter.py': os.path.join(base_dir, "scraper", "deepseek_filter.py")
        }
        
        # Check if all scripts exist
        missing_scripts = []
        for name, path in direct_paths.items():
            if not os.path.exists(path):
                missing_scripts.append(f"{name} ({path})")
        
        if missing_scripts:
            error_msg = f"The following scraper scripts were not found:\n{', '.join(missing_scripts)}"
            QMessageBox.critical(self, "Error", error_msg)
            return
        
        # Debug message
        print("Found all scraper scripts:")
        for name, path in direct_paths.items():
            print(f"- {name}: {path}")
        
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
        thread = threading.Thread(target=self.run_scraper, args=(direct_paths, progress))
        thread.start()

    def run_scraper(self, scripts_to_use, progress_dialog):
        import subprocess, sys, os
        try:
            # Set up environment variables for resource paths with absolute paths
            env = os.environ.copy()
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Use direct paths for data files rather than resource_path
            tender_data_path = os.path.join(base_dir, "tender_data")
            last_id_path = os.path.join(base_dir, "last_id.txt")
            keywords_path = os.path.join(base_dir, "tender_data", "Tender_Keywords.csv")
            
            env["TENDER_DATA_PATH"] = tender_data_path
            env["LAST_ID_PATH"] = last_id_path
            env["KEYWORDS_PATH"] = keywords_path
            env["NO_UI"] = "1"  # Prevent UI initialization in subprocess
            
            # Print debug info
            print(f"Running scrapers with paths:")
            print(f"TENDER_DATA_PATH: {tender_data_path}")
            print(f"LAST_ID_PATH: {last_id_path}")
            print(f"KEYWORDS_PATH: {keywords_path}")
            
            # Use Python executable from current virtual environment
            python_exe = sys.executable
            print(f"Using Python: {python_exe}")
            
            # Run scripts in sequence
            script_sequence = ['scraper.py', 'scraper_links.py', 'deepseek_filter.py']
            success = True
            error_messages = []
            
            for script_name in script_sequence:
                script_path = scripts_to_use[script_name]
                self.progress_text = f"Running {script_name}..."
                print(f"Running: {python_exe} {script_path}")
                
                result = subprocess.run(
                    [python_exe, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                # Print outputs for debugging
                print(f"\n--- {script_name} stdout ---")
                print(result.stdout)
                print(f"\n--- {script_name} stderr ---")
                print(result.stderr)
                
                if result.returncode != 0:
                    error_message = f"{script_name} failed with exit status {result.returncode}\n"
                    error_message += f"STDERR: {result.stderr}\n"
                    error_message += f"STDOUT: {result.stdout}"
                    error_messages.append(error_message)
                    success = False
                    break
            
        except Exception as e:
            import traceback
            success = False
            error_messages.append(f"Exception: {str(e)}\n{traceback.format_exc()}")
        
        # Finish progress on the main thread
        QTimer.singleShot(0, lambda: self.scraping_finished(
            success, 
            "\n\n".join(error_messages), 
            progress_dialog
        ))

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
                # Try both possible CSV files
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                filtered_path = os.path.join(base_dir, "tender_data", "filtered_tenders.csv")
                regular_path = os.path.join(base_dir, "tender_data", "tender_data.csv")
                
                if os.path.exists(filtered_path):
                    self.csv_file = filtered_path
                elif os.path.exists(regular_path):
                    self.csv_file = regular_path
                
                print(f"Loading tender data from: {self.csv_file}")
                
                self.model = self.load_csv_model()
                self.ui.TenderList.setModel(self.model)
                QMessageBox.information(self, "Success", "Tenders have been scraped and updated successfully.")
            except Exception as e:
                import traceback
                error_detail = f"Error reloading tender data: {str(e)}\n\n{traceback.format_exc()}"
                print(error_detail)
                QMessageBox.critical(self, "Error", error_detail)
        else:
            QMessageBox.critical(self, "Error", f"Error occurred while scraping tenders:\n{error_message}")
            print(f"Scraping error: {error_message}")

    def clean_ai_response(self, text):
        """
        Remove common AI response artifacts like "/thinking" markers, JSON structures, etc.
        """
        # Remove lines starting with "/" often used for AI thinking/reasoning
        lines = text.split('\n')
        clean_lines = []
        
        # Flag to track if we're inside a thinking/internal monologue block
        in_thinking_block = False
        # Flag to track if we're inside a JSON/code block
        in_json_block = False
        # Flag to track if we've started collecting real content
        content_started = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check for thinking/reasoning blocks starting patterns
            if (line_lower.startswith('/') or 
                line_lower.startswith('thinking:') or 
                line_lower.startswith('[thinking]') or
                '</think>' in line_lower or
                line_lower.startswith('thinking ')):
                in_thinking_block = True
                continue
                
            # Check for end of thinking block
            if in_thinking_block and (line_lower == '' or line_lower.startswith('#') or line_lower.startswith('---')):
                in_thinking_block = False
                continue
                
            # Skip lines inside thinking blocks
            if in_thinking_block:
                continue
                
            # Check for JSON/code block patterns
            if (line_lower.startswith('{') and ('"' in line_lower or ':' in line_lower)) or line_lower.startswith('[{'):
                in_json_block = True
                continue
                
            # Check for end of JSON block
            if in_json_block and (line_lower.endswith('}') or line_lower.endswith('],') or line_lower.endswith(']}')) or line_lower.endswith('}'):
                in_json_block = False
                continue
                
            # Skip lines inside JSON blocks
            if in_json_block:
                continue
                
            # Remove other markdown artifacts often used by AI models
            if (line_lower.startswith('```') or 
                line_lower.startswith('**note:**') or 
                line_lower == '<answer>' or 
                line_lower == '</answer>' or
                '<|' in line_lower and '|>' in line_lower or
                line_lower.startswith('usage:') or
                line_lower.startswith('prompt_tokens:') or
                line_lower.startswith('completion_tokens:') or
                line_lower.startswith('total_tokens:') or
                line_lower.startswith('response:') or
                line_lower.startswith('stats:') or
                line_lower.startswith('system_fingerprint:')) or line_lower.startswith('###'):
                continue

            # Skip any lines that look like JSON keys or values in API responses
            if (': {' in line or ': [' in line or 
                line_lower.strip() == '},' or 
                line_lower.strip() == '],' or
                ('"' in line and ':' in line and line.strip().endswith(','))):
                continue
                
            # Lines likely to be real content
            if len(line_lower) > 0:
                content_started = True
            
            # Only add non-empty lines once content has started
            if content_started:
                clean_lines.append(line)
        
        # Join cleaned lines back together
        cleaned_text = '\n'.join(clean_lines)
        
        # Remove multiple consecutive blank lines
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
            
        # Remove any trailing "Tender rejected:" text which might be part of the template
        if "Tender rejected:" in cleaned_text and len(cleaned_text.split("Tender rejected:")) > 1:
            # Keep only the part after "Tender rejected:" as that's likely the actual decision
            cleaned_text = "Tender rejected: " + cleaned_text.split("Tender rejected:")[1].strip()
        
        return cleaned_text.strip()

def run_ui():
    app = QApplication(sys.argv)
    main_window = TenderBackend()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_ui()
