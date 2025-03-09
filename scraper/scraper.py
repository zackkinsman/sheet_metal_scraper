import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from datetime import datetime

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--start-maximized')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    driver = webdriver.Chrome(options=options)
    return driver

def load_keywords(csv_path):
    df = pd.read_csv(csv_path)
    return df.iloc[:, 1].tolist()  # Selecting the second column for keywords

def get_last_id():
    """Retrieve the last used tender ID from a file; if the file doesn't exist, return 0."""
    if os.path.exists("last_id.txt"):
        with open("last_id.txt", "r") as f:
            try:
                last_id = int(f.read().strip())
            except ValueError:
                last_id = 0
    else:
        last_id = 0
    return last_id

def update_last_id(last_id):
    """Update the file with the new last used tender ID."""
    with open("last_id.txt", "w") as f:
        f.write(str(last_id))

def search_tenders(driver, keywords):
    driver.get("https://canadabuys.canada.ca/en")

    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Search tenders"))
    )
    search_button.click()

    all_data = []
    # Retrieve the last used ID from persistence.
    tender_id = get_last_id()

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

        # Process only one keyword for now; remove break to iterate through all keywords.
        break

    # Save backup CSV with standardized name
    csv_filename = "tender_data/tender_data.csv"
    df = pd.DataFrame(all_data)
    df.to_csv(csv_filename, index=False)
    print(f"Backup CSV saved as {csv_filename}")

    # Update the persistent last_id file with the latest ID used.
    update_last_id(tender_id)

def main():
    driver = setup_driver()
    keywords = load_keywords("c:\\Users\\Zack\\Desktop\\School stuff\\Sheet_Metal_Project\\sheet_metal_scraper\\Tender_Keywords.csv")

    try:
        search_tenders(driver, keywords)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()