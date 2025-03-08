import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from datetime import datetime

# Import ReportLab modules for PDF conversion.
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
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
            tender_id += 1  # Increment the ID for each new tender
            row_data = {
                "id": tender_id,
                "title": title_cell.text,
                "link": title_cell.get_attribute("href"),
                "category": cells[1].text,
                "date_posted": cells[2].text,   # Open/Amendment Date
                "closing_date": cells[3].text,
                "organization": cells[4].text
            }
            all_data.append(row_data)

        # Process only one keyword for now; remove break to iterate through all keywords.
        break

    # Save backup CSV with timestamp
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"tender_data_{current_datetime}.csv"
    df = pd.DataFrame(all_data)
    df.to_csv(csv_filename, index=False)
    print(f"Backup CSV saved as {csv_filename}")

    # Convert CSV to PDF
    pdf_filename = f"tender_data_{current_datetime}.pdf"
    convert_csv_to_pdf(csv_filename, pdf_filename)
    print(f"PDF file saved as {pdf_filename}")

    # Update the persistent last_id file with the latest ID used.
    update_last_id(tender_id)

def convert_csv_to_pdf(csv_filename, pdf_filename):
    # Read CSV file
    df = pd.read_csv(csv_filename)
    data = [df.columns.tolist()] + df.values.tolist()

    # Create PDF document
    pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)
    table = Table(data)
    
    # Apply simple styling
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.gray),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    table.setStyle(style)
    elements = [table]
    pdf.build(elements)

def main():
    driver = setup_driver()
    keywords = load_keywords("../Tender_Keywords.csv")

    try:
        search_tenders(driver, keywords)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
