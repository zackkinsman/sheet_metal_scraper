#!/usr/bin/env python
import sys
import traceback
import logging
from UI.tender_backend import run_ui
from UI import resource_path

# Configure logging to capture errors
LOG_FILE = resource_path("error.log")
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    try:
        run_ui()
    except Exception as e:
        error_message = f"An unhandled exception occurred: {e}\n{traceback.format_exc()}"
        print(error_message)  # This will show in console if run from CMD
        logging.error(error_message)  # Logs to file
        sys.exit(1)

if __name__ == "__main__":
    main()
