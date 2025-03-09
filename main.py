#!/usr/bin/env python
import sys
from UI.tender_backend import run_ui

def main():
    try:
        run_ui()
    except Exception as e:
        print("An unhandled exception occurred:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
