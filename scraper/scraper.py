import os
import sys
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from datetime import datetime
import traceback

def get_path(env_var, default_path):
    """Get path from environment variable or fall back to default"""
    return os.getenv(env_var, default_path)

# Only import from UI if not running as subprocess
if not os.getenv("NO_UI"):
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from UI import resource_path
else:
    def resource_path(relative_path):
        """Replacement for UI.resource_path when running as subprocess"""
        return get_path("TENDER_DATA_PATH", relative_path)

def setup_driver():
    log_path = os.path.join(os.path.expanduser("~"), "Desktop", "selenium_debug.log")
    try:
        with open(log_path, "a") as f:
            f.write(f"=== Setting up Selenium driver - {datetime.now()} ===\n")
            
            # Try to detect Chrome location
            f.write("Looking for Chrome...\n")
            chrome_paths = [
                os.path.expandvars("%ProgramFiles%\\Google\\Chrome\\Application\\chrome.exe"),
                os.path.expandvars("%ProgramFiles(x86)%\\Google\\Chrome\\Application\\chrome.exe"),
                os.path.expandvars("%LocalAppData%\\Google\\Chrome\\Application\\chrome.exe")
            ]
            
            chrome_path = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_path = path
                    f.write(f"Found Chrome at: {path}\n")
                    break
            
            if not chrome_path:
                f.write("Chrome not found in standard locations\n")
            
            # Find chromedriver.exe - check bundled location first, then fallback to project root
            chromedriver_paths = [
                get_path("CHROMEDRIVER_PATH", "chromedriver-win64/chromedriver.exe"),  # Bundled location
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chromedriver-win64", "chromedriver.exe"),  # Project root location
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chromedriver.exe"),  # Directly in project root
            ]
            
            chromedriver_path = None
            for path in chromedriver_paths:
                f.write(f"Checking for ChromeDriver at: {path}\n")
                if os.path.exists(path):
                    chromedriver_path = path
                    f.write(f"Found ChromeDriver at: {path}\n")
                    break
            
            if not chromedriver_path:
                f.write("ERROR: ChromeDriver not found in expected locations!\n")
                raise FileNotFoundError("ChromeDriver not found. Please ensure it is bundled correctly.")
            
            f.write(f"Attempting to create ChromeDriver with service path: {chromedriver_path}\n")
        
        # Set up ChromeDriver options
        options = webdriver.ChromeOptions()
        if chrome_path:
            options.binary_location = chrome_path
        
        # Add options for headless and performance settings
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--start-maximized')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Create the driver using the found ChromeDriver path
        from selenium.webdriver.chrome.service import Service
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        with open(log_path, "a") as f:
            f.write("ChromeDriver created successfully!\n")
            
        return driver
        
    except Exception as e:
        with open(log_path, "a") as f:
            f.write(f"Error setting up ChromeDriver: {str(e)}\n")
            f.write(traceback.format_exc())
        raise

def load_keywords(csv_path):
    df = pd.read_csv(csv_path)
    # Assumes that keywords are in the second column of the CSV
    return df.iloc[:, 1].tolist()

def get_last_id():
    """Retrieve the last used tender ID from a file; if the file doesn't exist, return 0."""
    last_id_path = get_path("LAST_ID_PATH", "last_id.txt")
    if os.path.exists(last_id_path):
        with open(last_id_path, "r") as f:
            try:
                last_id = int(f.read().strip())
            except ValueError:
                last_id = 0
    else:
        last_id = 0
    return last_id

def update_last_id(last_id):
    """Update the file with the new last used tender ID."""
    last_id_path = get_path("LAST_ID_PATH", "last_id.txt")
    with open(last_id_path, "w") as f:
        f.write(str(last_id))

def search_tenders(driver, keywords):
    driver.get("https://canadabuys.canada.ca/en")
    
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Search tenders"))
    )
    search_button.click()
    
    all_data = []
    tender_id = get_last_id()  # Retrieve the last used ID

    for keyword in keywords:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "edit-words--7"))
        )
        search_box.clear()
        search_box.send_keys(keyword)
        
        time.sleep(random.uniform(3, 6))  # Simulate human interaction
        
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-twig-selector='search']"))
        )
        search_button.click()
        
        time.sleep(random.uniform(5, 10))
        
        table_body = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
        )
        rows = table_body.find_elements(By.TAG_NAME, "tr")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            title_cell = cells[0].find_element(By.TAG_NAME, "a")
            organization = cells[4].text
            if organization == "NATO - North Atlantic Treaty Organization":
                continue  # Skip this tender
            tender_id += 1  # Increment the ID for each new tender
            row_data = {
                "id": tender_id,
                "title": title_cell.text,
                "link": title_cell.get_attribute("href"),
                "category": cells[1].text,
                "date_posted": cells[2].text,   # Open/Amendment Date
                "closing_date": cells[3].text,
                "organization": organization
            }
            all_data.append(row_data)
        
        # Currently processing only one keyword; remove the break to iterate through all keywords.
        break

    csv_filename = os.path.join(get_path("TENDER_DATA_PATH", "tender_data"), "tender_data.csv")
    df = pd.DataFrame(all_data)
    df.to_csv(csv_filename, index=False)
    print(f"Backup CSV saved as {csv_filename}")
    
    update_last_id(tender_id)

def main():
    log_path = os.path.join(os.path.expanduser("~"), "Desktop", "scraper_error.log")
    try:
        with open(log_path, "a") as f:
            f.write("\nStarting scraper.py main function\n")
        
        driver = setup_driver()
        keywords = load_keywords(get_path("KEYWORDS_PATH", "tender_data/Tender_Keywords.csv"))
        
        try:
            search_tenders(driver, keywords)
        except Exception as e:
            with open(log_path, "a") as f:
                f.write(f"Error during search_tenders: {str(e)}\n")
                f.write(traceback.format_exc())
            raise
        finally:
            driver.quit()
            
    except Exception as e:
        with open(log_path, "a") as f:
            f.write(f"Error in main function: {str(e)}\n")
            f.write(traceback.format_exc())

if __name__ == "__main__":
    main()
