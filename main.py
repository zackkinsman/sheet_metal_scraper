#!/usr/bin/env python
import sys
from UI.tender_backend import run_ui

def main():
    """
    Main entry point for the Tender Application.

    This function initializes the UI by calling run_ui() from the tender_backend module.
    The tender_backend module handles:
      - Database connection and ensuring the bundled tenders.db is copied to a writable location.
      - Setting up the QSqlTableModel and loading the UI.
    
    Note: For the POC, any additional threads (such as a scraper thread) are currently disabled.
    """
    try:
        run_ui()
    except Exception as e:
        print("An unhandled exception occurred:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
