from ui.tender_backend import run_ui  # PyQt app
from scraper.scraper import scrape_tenders  # Selenium scraper
import threading

def main():
    # Run the scraper in a separate thread
    scraper_thread = threading.Thread(target=scrape_tenders, daemon=True)
    scraper_thread.start()

    # Launch UI
    run_ui()

if __name__ == "__main__":
    main()
