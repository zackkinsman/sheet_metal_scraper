import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from datetime import datetime

# Import the insert_tender function from the PostgreSQL database module
from db.database import insert_tender

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    return driver

def load_keywords(csv_path):
    df = pd.read_csv(csv_path)
    return df.iloc[:, 1].tolist()  # Selecting the second column for keywords

def search_tenders(driver, keywords):
    driver.get("https://canadabuys.canada.ca/en")

    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Search tenders"))
    )
    search_button.click()

    all_data = []

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
            row_data = {
                "title": title_cell.text,
                "description": title_cell.get_attribute("title"),
                "link": title_cell.get_attribute("href"),
                "category": cells[1].text,
                # Scraped value from cells[2] is the Open/Amendment Date, so we store it in date_posted.
                "date_posted": cells[2].text,
                "closing_date": cells[3].text,
                "organization": cells[4].text
            }
            all_data.append(row_data)

            # Insert the tender into the PostgreSQL database.
            insert_tender(
                title=row_data["title"],
                description=row_data["description"],
                date_posted=row_data["date_posted"],
                closing_date=row_data["closing_date"],
                link=row_data["link"],
                status="New"
            )

        # Process only one keyword for now; remove break to iterate through all keywords.
        break

    # Save backup CSV with timestamp
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tender_data_{current_datetime}.csv"
    df = pd.DataFrame(all_data)
    df.to_csv(filename, index=False)
    print(f"Backup CSV saved as {filename}")

def main():
    driver = setup_driver()
    keywords = load_keywords("../Tender_Keywords.csv")

    try:
        search_tenders(driver, keywords)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
