import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

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

def main():
    driver = setup_driver()
    keywords = load_keywords("../Tender_Keywords.csv")

    try:
        search_tenders(driver, keywords)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()