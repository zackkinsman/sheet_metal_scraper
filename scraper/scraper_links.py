import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

# Removed the PDF extraction function

def extract_links_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    links = df['link'].tolist()
    print(links)
    return links

csv_path = "c:/Users/Zack/Desktop/School stuff/Sheet_Metal_Project/sheet_metal_scraper/tender_data/tender_data.csv"
extract_links_from_csv(csv_path)

# def scrape_tender_details(url):
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#     driver.get(url)
#     try:
#         description_div = driver.find_element(By.CLASS_NAME, 'field--name-body')
#         description = description_div.text
#     except NoSuchElementException:
#         description = "Element not found"
#         print(f"Element with class 'field--name-body' not found on {url}")
#     driver.quit()
#     return description

# def main():
#     pdf_filename = os.path.join(os.path.dirname(__file__), "..", "tender_data", "tender_data.pdf")
#     csv_path = os.path.join(os.path.dirname(__file__), "..", "tender_data", "tender_data.csv")
#     new_csv_path = os.path.join(os.path.dirname(__file__), "..", "tender_data", "tender_data_with_descriptions.csv")
#     new_pdf_path = os.path.join(os.path.dirname(__file__), "..", "tender_data", "tender_data_with_descriptions.pdf")
    
#     # Read existing CSV
#     df = pd.read_csv(csv_path)
    
#     # Extract links from PDF
#     pdf_links = extract_links_from_pdf(pdf_filename)
    
#     # Scrape descriptions for links in the CSV
#     descriptions = [scrape_tender_details(link) for link in df['link']]
#     df['Full Description'] = descriptions
    
#     # Save the updated CSV
#     df.to_csv(new_csv_path, index=False)
    
#     # Convert the new CSV to PDF
#     convert_csv_to_pdf(new_csv_path, new_pdf_path)
#     print(f"New CSV file saved as {new_csv_path}")
#     print(f"New PDF file saved as {new_pdf_path}")

# if __name__ == "__main__":
#     main()