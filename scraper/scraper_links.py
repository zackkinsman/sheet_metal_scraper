import os
import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_links_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    links = df['link'].tolist()
    return links

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--start-maximized')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_tender_details(url):
    driver = setup_driver()
    driver.get(url)
    try:
        # Use a CSS selector for the unique class "tender-detail-description"
        description_div = driver.find_element(By.CSS_SELECTOR, "div.tender-detail-description")
        description = description_div.text
        time.sleep(random.uniform(1, 3))  # Random delay between 1 to 3 seconds
    except NoSuchElementException:
        description = "Element not found"
        print(f"Element with class 'tender-detail-description' not found on {url}")
    driver.quit()
    return description

def scrape_batch(links):
    descriptions = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(scrape_tender_details, link): link for link in links}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                description = future.result()
                time.sleep(random.uniform(1, 3))  # Random delay between 1 to 3 seconds
            except Exception as exc:
                description = "Error occurred"
                print(f"Error occurred while scraping {url}: {exc}")
            descriptions[url] = description
    return descriptions

def main():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "tender_data", "tender_data.csv")
    new_csv_path = os.path.join(os.path.dirname(__file__), "..", "tender_data", "tender_data_with_descriptions.csv")
    
    # Read existing CSV
    df = pd.read_csv(csv_path)
    
    # Extract links from CSV
    links = extract_links_from_csv(csv_path)
    
    # Scrape descriptions in batches
    descriptions = scrape_batch(links)
    
    # Append the descriptions to the DataFrame
    for link, description in descriptions.items():
        df.loc[df['link'] == link, 'Full Description'] = description
    
    # Save the updated CSV
    df.to_csv(new_csv_path, index=False)
    print(f"New CSV file saved as {new_csv_path}")

if __name__ == "__main__":
    main()