import os
import sys
import pandas as pd
import time
import random
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path to import the resource_path function
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from UI import resource_path

def extract_links_from_csv(csv_path):
    try:
        df = pd.read_csv(csv_path)
        links = df['link'].tolist()
        return links
    except Exception as e:
        log_error(f"Error extracting links from CSV: {str(e)}")
        return []

def log_error(message):
    """Write error message to log file on desktop"""
    log_file = os.path.join(os.path.expanduser("~"), "Desktop", "scraper_error.log")
    try:
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception as e:
        print(f"Failed to write to log file: {e}")

def setup_driver():
    try:
        # Log the setup process for debugging
        log_file = os.path.join(os.path.expanduser("~"), "Desktop", "selenium_debug.log")
        with open(log_file, "a") as f:
            f.write(f"=== Setting up Selenium driver for scraper_links - {datetime.now()} ===\n")
            
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
            
            # Find chromedriver.exe - First check bundled location, then fallback to project root
            chromedriver_paths = [
                resource_path("chromedriver-win64/chromedriver.exe"),  # Bundled location
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
                raise FileNotFoundError("ChromeDriver not found in expected locations.")
            
            f.write(f"Attempting to create ChromeDriver with service path: {chromedriver_path}\n")
        
        options = webdriver.ChromeOptions()
        
        # Set specific Chrome binary path if found
        if chrome_path:
            options.binary_location = chrome_path
            
        # Add options to make Chrome more reliable in this context
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--start-maximized')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Try to create the driver with the specific chromedriver path
        from selenium.webdriver.chrome.service import Service
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        with open(log_file, "a") as f:
            f.write("ChromeDriver created successfully!\n")
            
        return driver
        
    except Exception as e:
        log_error(f"Error setting up ChromeDriver in scraper_links.py: {str(e)}")
        log_error(traceback.format_exc())
        raise

def scrape_tender_details(url):
    driver = None
    try:
        driver = setup_driver()
        driver.get(url)
        # Use a CSS selector for the unique class "tender-detail-description"
        description_div = driver.find_element(By.CSS_SELECTOR, "div.tender-detail-description")
        description = description_div.text
        time.sleep(random.uniform(1, 3))  # Random delay between 1 to 3 seconds
    except NoSuchElementException:
        description = "Element not found"
        log_error(f"Element with class 'tender-detail-description' not found on {url}")
    except Exception as e:
        description = f"Error scraping details: {str(e)}"
        log_error(f"Error scraping details from {url}: {str(e)}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                log_error(f"Error quitting driver for {url}: {str(e)}")
    return description

def scrape_batch(links):
    descriptions = {}
    max_workers = min(5, len(links))  # Use fewer threads to be gentler
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(scrape_tender_details, link): link for link in links}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    description = future.result()
                    time.sleep(random.uniform(1, 3))  # Random delay between 1 to 3 seconds
                except Exception as exc:
                    description = "Error occurred"
                    log_error(f"Error occurred while scraping {url}: {exc}")
                descriptions[url] = description
    except Exception as e:
        log_error(f"Error in thread pool execution: {str(e)}")
        log_error(traceback.format_exc())
    
    return descriptions

def main():
    log_error("\n=== Starting scraper_links.py main function ===")
    
    try:
        csv_path = resource_path("tender_data/tender_data.csv")
        new_csv_path = resource_path("tender_data/tender_data_with_descriptions.csv")
        
        log_error(f"Reading from CSV path: {csv_path}")
        log_error(f"Will write to CSV path: {new_csv_path}")
        
        # Read existing CSV
        df = pd.read_csv(csv_path)
        
        # Extract links from CSV
        links = extract_links_from_csv(csv_path)
        log_error(f"Extracted {len(links)} links from CSV")
        
        if not links:
            log_error("No links found in CSV file")
            raise ValueError("No links found in CSV file")
        
        # Scrape descriptions in batches
        log_error(f"Starting to scrape descriptions for {len(links)} links")
        descriptions = scrape_batch(links)
        log_error(f"Scraped {len(descriptions)} descriptions")
        
        # Append the descriptions to the DataFrame
        for link, description in descriptions.items():
            df.loc[df['link'] == link, 'Full Description'] = description
        
        # Save the updated CSV
        df.to_csv(new_csv_path, index=False)
        log_error(f"New CSV file saved as {new_csv_path}")

    except Exception as e:
        log_error(f"Error in main function: {str(e)}")
        log_error(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()
