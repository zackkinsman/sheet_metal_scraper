import requests
import pandas as pd
import os
import sys
import json
import time
from datetime import datetime

# Add parent directory to path to import the resource_path function
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from UI import resource_path

# API details
DEEPSEEK_API_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "deepseek-r1-distill-qwen-7b"

def load_capabilities():
    """Load plant capabilities from a text file"""
    capabilities_path = resource_path("tender_data/mulgrave_capabilities.txt")
    if not os.path.exists(capabilities_path):
        return None
    try:
        with open(capabilities_path, "r") as f:
            return f.read().strip()
    except Exception:
        return None

def load_tender_data():
    """Load the tender data from the CSV file into a pandas DataFrame"""
    try:
        tender_data_path = resource_path("tender_data/tender_data_with_descriptions.csv")
        return pd.read_csv(tender_data_path)
    except Exception:
        return None

def deepseek_filter(tenders):
    capabilities = load_capabilities()
    if capabilities is None or tenders is None:
        print("Error: Failed to load capabilities or tenders")
        return None

    filtered_tenders = []
    for _, tender in tenders.iterrows():
        try:
            # Check if the required field exists
            description = tender.get('Full Description')
            if not description:
                print(f"Warning: Missing description for tender {tender.get('title', 'No title')}")
                continue

            # Prepare the prompt
            prompt = f"""Given the following tender description and company capabilities, determine if this tender is relevant. Only respond with 'yes' or 'no'.

Tender: {description}

Company Capabilities:
{capabilities}"""

            print(f"Sending request to DeepSeek API...")
            
            # Call the DeepSeek API
            response = requests.post(
                DEEPSEEK_API_URL,
                headers={"Content-Type": "application/json"},
                json={
                    "model": MODEL_NAME,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": -1,
                    "stream": False
                },
                timeout=30  # Add timeout to avoid hanging
            )
            
            print(f"API Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"API Response: {result}")
                answer = result['choices'][0]['message']['content'].strip().lower()
                
                if answer == 'yes':
                    filtered_tenders.append(tender)
                    print(f"Tender accepted: {tender.get('title', 'No title')}")
                else:
                    print(f"Tender rejected: {tender.get('title', 'No title')}")
            else:
                print(f"Error response from API: {response.text}")
            
            time.sleep(1)  # Rate limiting
            
        except requests.exceptions.ConnectionError:
            print(f"Connection Error: Could not connect to {DEEPSEEK_API_URL}. Is the API server running?")
            return None
        except Exception as e:
            print(f"Error processing tender: {str(e)}")
            continue

    if filtered_tenders:
        df = pd.DataFrame(filtered_tenders)
        output_path = resource_path("tender_data/filtered_tenders.csv")
        df.to_csv(output_path, index=False)
        return df
    return None

if __name__ == "__main__":
    try:
        print("Starting DeepSeek filter process...")
        tenders = load_tender_data()
        if tenders is not None:
            result = deepseek_filter(tenders)
            if result is None:
                print("Filter process failed or no tenders were accepted")
            else:
                print(f"Successfully filtered tenders. Found {len(result)} matching tenders.")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)
