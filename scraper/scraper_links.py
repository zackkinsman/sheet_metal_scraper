import os
import sys
import pandas as pd
import time
import random
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
        return df['link'].tolist()
    except Exception:
        return []

def setup_driver():
    # Try to detect Chrome location
    chrome_paths = [
        os.path.expandvars("%ProgramFiles%\\Google\\Chrome\\Application\\chrome.exe"),
        os.path.expandvars("%ProgramFiles(x86)%\\Google\\Chrome\\Application\\chrome.exe"),
        os.path.expandvars("%LocalAppData%\\Google\\Chrome\\Application\\chrome.exe")
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break
    
    # Find chromedriver.exe - First check bundled location, then fallback to project root
    chromedriver_paths = [
        resource_path("chromedriver-win64/chromedriver.exe"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chromedriver-win64", "chromedriver.exe"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chromedriver.exe"),
    ]
    
    chromedriver_path = None
    for path in chromedriver_paths:
        if os.path.exists(path):
            chromedriver_path = path
            break
    
    if not chromedriver_path:
        raise FileNotFoundError("ChromeDriver not found in expected locations.")
    
    options = webdriver.ChromeOptions()
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
    
    # Create the driver with the specific chromedriver path
    from selenium.webdriver.chrome.service import Service
    service = Service(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=options)

def scrape_tender_details(url):
    driver = None
    try:
        driver = setup_driver()
        driver.get(url)
        # Use a CSS selector for the unique class "tender-detail-description"
        description_div = driver.find_element(By.CSS_SELECTOR, "div.tender-detail-description")
        description = description_div.text
        time.sleep(random.uniform(1, 3))  # Random delay between 1 to 3 seconds
        return description
    except NoSuchElementException:
        return "Element not found"
    except Exception as e:
        return f"Error scraping details: {str(e)}"
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

def scrape_batch(links):
    descriptions = {}
    max_workers = min(5, len(links))  # Use fewer threads to be gentler
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(scrape_tender_details, link): link for link in links}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                description = future.result()
                time.sleep(random.uniform(1, 3))  # Random delay between 1 to 3 seconds
            except Exception:
                description = "Error occurred"
            descriptions[url] = description
    
    return descriptions

def main():
    try:
        csv_path = resource_path("tender_data/tender_data.csv")
        new_csv_path = resource_path("tender_data/tender_data_with_descriptions.csv")
        
        # Read existing CSV
        df = pd.read_csv(csv_path)
        
        # Extract links from CSV
        links = extract_links_from_csv(csv_path)
        
        if not links:
            raise ValueError("No links found in CSV file")
        
        # Scrape descriptions in batches
        descriptions = scrape_batch(links)
        
        # Append the descriptions to the DataFrame
        for link, description in descriptions.items():
            df.loc[df['link'] == link, 'Full Description'] = description
        
        # Save the updated CSV
        df.to_csv(new_csv_path, index=False)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
