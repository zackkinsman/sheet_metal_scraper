import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from datetime import datetime  # Add this import

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

        time.sleep(random.uniform(3, 6))  # simulate human interaction and avoid bot detection

        # Click the search button after entering the keyword
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-twig-selector='search']"))
        )
        search_button.click()

        # Allow results to load before moving to the next keyword
        time.sleep(random.uniform(5, 10))

        # Extract table data
        table_body = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
        )
        rows = table_body.find_elements(By.TAG_NAME, "tr")

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            title_cell = cells[0].find_element(By.TAG_NAME, "a")
            row_data = {
                "Title": title_cell.text,
                "Full Description": title_cell.get_attribute("title"),
                "Link": title_cell.get_attribute("href"),
                "Category": cells[1].text,
                "Publication Date": cells[2].text,
                "Closing Date": cells[3].text,
                "Organization": cells[4].text
            }
            all_data.append(row_data)

        # Comment out the "Load more results" button handling
        # while True:
        #     try:
        #         load_more_button = WebDriverWait(driver, 10).until(
        #             EC.element_to_be_clickable((By.CSS_SELECTOR, "a[rel='next']"))
        #         )
        #         load_more_button.click()
        #         time.sleep(random.uniform(5, 10))  # Wait for additional results to load
        #     except:
        #         break  # No more "Load more results" button

        break  # Comment out the part that keeps searching

    # Save data to CSV with datetime in filename
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"C:/Users/Zack/Desktop/School stuff/Sheet_Metal_Project/sheet_metal_scraper/tender_data_{current_datetime}.csv"
    df = pd.DataFrame(all_data)
    df.to_csv(filename, index=False)

def main():
    driver = setup_driver()
    keywords = load_keywords("../Tender_Keywords.csv")

    try:
        search_tenders(driver, keywords)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()