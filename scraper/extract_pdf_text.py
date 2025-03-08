import fitz  # PyMuPDF
import os

# Function to extract text from PDF

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

if __name__ == "__main__":
    pdf_path = "C:\\Users\\Zack\\Desktop\\School stuff\\Sheet_Metal_Project\\sheet_metal_scraper\\tender_data\\tender_csv - tender_data_20250303_195411.pdf"
    extracted_text = extract_text_from_pdf(pdf_path)
    print(extracted_text)