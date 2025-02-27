# main.py
from tender_backend import run_ui

def main():
    # For the POC, we can ignore the scraper thread
    run_ui()

if __name__ == "__main__":
    main()
