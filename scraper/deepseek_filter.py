import requests
import pandas as pd
import os
import sys
import json
import traceback
import time
from datetime import datetime

# Add parent directory to path to import the resource_path function
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from UI import resource_path

# API details (update if needed)
DEEPSEEK_API_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "deepseek-r1-distill-qwen-7b"

def log_error(message):
    """Write error message to log file on desktop"""
    log_file = os.path.join(os.path.expanduser("~"), "Desktop", "scraper_error.log")
    try:
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [deepseek_filter.py] {message}\n")
    except Exception as e:
        print(f"Failed to write to log file: {e}")

def load_capabilities():
    """Load plant capabilities from a text file"""
    capabilities_path = resource_path("tender_data/mulgrave_capabilities.txt")
    if not os.path.exists(capabilities_path):
        error_msg = f"Error: Could not find plant capabilities file at {capabilities_path}"
        log_error(error_msg)
        return None
    try:
        with open(capabilities_path, "r") as f:
            return f.read().strip()
    except Exception as e:
        error_msg = f"Error loading plant capabilities: {e}"
        log_error(error_msg)
        return None

def load_tender_data():
    """Load the tender data from the CSV file into a pandas DataFrame"""
    tender_descriptions_path = resource_path("tender_data/tender_data_with_descriptions.csv")
    if not os.path.exists(tender_descriptions_path):
        error_msg = f"Error: Could not find tender data file at {tender_descriptions_path}"
        log_error(error_msg)
        return pd.DataFrame()
    try:
        df = pd.read_csv(tender_descriptions_path)
        return df
    except Exception as e:
        error_msg = f"Error loading tender data: {e}"
        log_error(error_msg)
        return pd.DataFrame()

def write_debug_log(message):
    """Write debug information to a log file"""
    debug_log_path = resource_path("tender_data/filter_debug.log")
    try:
        with open(debug_log_path, "a", encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception as e:
        log_error(f"Warning: Could not write to debug log: {e}")

def deepseek_filter(tenders):
    """
    Sends tenders to DeepSeek AI and filters out irrelevant ones.
    Creates a CSV file with all relevant tenders and their full information.
    Returns a list of tenders deemed relevant.
    """
    log_error("Starting deepseek_filter function")
    
    # Load plant capabilities
    PLANT_CAPABILITIES = load_capabilities()
    if not PLANT_CAPABILITIES:
        log_error("Error: Failed to load plant capabilities")
        raise ValueError("Failed to load plant capabilities")

    relevant_tenders = []
    relevant_ids = []
    
    # Clear previous debug log
    debug_log_path = resource_path("tender_data/filter_debug.log")
    try:
        with open(debug_log_path, "w", encoding='utf-8') as f:
            f.write(f"DeepSeek Filter Debug Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    except Exception as e:
        log_error(f"Warning: Could not create debug log: {e}")
    
    # Load full tender data from CSV
    all_tender_data = load_tender_data()
    if all_tender_data.empty:
        log_error("Error: Could not load tender data with descriptions")
        raise ValueError("Could not load tender data with descriptions")

    # Initialize API status
    api_available = False
    max_retries = 3
    retry_delay = 10  # seconds

    for retry in range(max_retries):
        try:
            test_payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "system", "content": "Test message"}],
                "temperature": 0.3
            }
            response = requests.post(DEEPSEEK_API_URL, json=test_payload, timeout=5)
            if response.status_code == 200:
                api_available = True
                log_error("API connectivity test successful")
                break
            else:
                log_error(f"API test failed (attempt {retry + 1}/{max_retries}): Status {response.status_code}")
        except Exception as e:
            log_error(f"API test failed (attempt {retry + 1}/{max_retries}): {str(e)}")
            if retry < max_retries - 1:
                log_error(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)

    if not api_available:
        log_error("WARNING: DeepSeek AI filtering unavailable. Processing without AI filtering.")
        # Save all tenders to filtered output without AI processing
        filtered_tenders_path = resource_path("tender_data/filtered_tenders.csv")
        try:
            all_tender_data.to_csv(filtered_tenders_path, index=False)
            log_error(f"Saved all {len(all_tender_data)} tenders without filtering to {filtered_tenders_path}")
            return tenders
        except Exception as e:
            log_error(f"Error saving unfiltered tenders: {e}")
            raise

    # Continue with AI filtering if API is available
    for tender in tenders:
        tender_id = tender.get('id')
        tender_row = all_tender_data[all_tender_data['id'] == tender_id]
        
        if not tender_row.empty:
            full_description = tender_row['Full Description'].iloc[0]
            tender_title = tender_row['title'].iloc[0]
        else:
            full_description = tender.get('description', "")
            tender_title = tender.get('title', "")
        
        tender_text = f"Title: {tender_title}\nDescription: {full_description}"

        prompt = f"""
        A manufacturing plant has the following capabilities:
        {PLANT_CAPABILITIES}
        
        Based on this, determine if the following tender is RELEVANT to the plant. 
        Respond with exactly one word: RELEVANT or NOT RELEVANT.

        Tender details:
        {tender_text}
        """

        try:
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "system", "content": "You analyze tenders for relevance."},
                            {"role": "user", "content": prompt}],
                "temperature": 0.3
            }

            write_debug_log(f"Processing tender ID: {tender_id} - {tender_title}")
            
            response = requests.post(DEEPSEEK_API_URL, json=payload, timeout=30)
            write_debug_log(f"API Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                write_debug_log(f"Raw AI response: '{ai_response}'")
                
                if "RELEVANT" in ai_response.upper() and "NOT RELEVANT" not in ai_response.upper():
                    write_debug_log(f"Tender {tender_id} marked as RELEVANT")
                    relevant_ids.append(tender_id)
                    relevant_tenders.append(tender)
                else:
                    write_debug_log(f"Tender {tender_id} marked as NOT RELEVANT")
            else:
                # If API fails during processing, mark tender as relevant to avoid missing opportunities
                write_debug_log(f"API error for tender {tender_id} - marking as potentially relevant")
                relevant_ids.append(tender_id)
                relevant_tenders.append(tender)

        except Exception as e:
            write_debug_log(f"Exception when processing tender {tender_id}: {str(e)}")
            log_error(f"Error processing tender {tender_id}: {e}")
            # Include tender if there's an error to avoid missing opportunities
            relevant_ids.append(tender_id)
            relevant_tenders.append(tender)
    
    # Save filtered results
    filtered_tenders_path = resource_path("tender_data/filtered_tenders.csv")
    try:
        if relevant_ids:
            filtered_data = all_tender_data[all_tender_data['id'].isin(relevant_ids)]
            filtered_data.to_csv(filtered_tenders_path, index=False)
            log_error(f"Found {len(relevant_ids)} relevant tenders. Data saved to {filtered_tenders_path}")
            write_debug_log(f"CSV saved with {len(relevant_ids)} relevant tenders")
        else:
            # Create empty filtered CSV if no relevant tenders
            empty_df = pd.DataFrame(columns=all_tender_data.columns)
            empty_df.to_csv(filtered_tenders_path, index=False)
            log_error("No relevant tenders found.")
            write_debug_log("Created empty filtered CSV as no tenders matched")
    except Exception as e:
        log_error(f"Error saving filtered results: {e}")
        raise

    return relevant_tenders

# Standalone script functionality
if __name__ == "__main__":
    log_error("\n=== Starting deepseek_filter.py main function ===")
    
    try:
        # Load all tenders from the CSV file
        all_tender_data = load_tender_data()
        
        if all_tender_data.empty:
            log_error("Error: Failed to load tender data")
            raise ValueError("Failed to load tender data")
        
        # Convert CSV data to the format expected by deepseek_filter
        tenders_to_process = []
        for _, row in all_tender_data.iterrows():
            tender = {
                'id': row['id'],
                'title': row['title'],
                'description': row.get('Full Description', '')
            }
            tenders_to_process.append(tender)
        
        log_error(f"Loaded {len(tenders_to_process)} tenders from CSV. Processing with AI filter...")
        
        # Filter tenders using DeepSeek AI
        relevant_tenders = deepseek_filter(tenders_to_process)
        
        # Print summary
        log_error(f"Final results: {len(relevant_tenders)} relevant tenders identified out of {len(tenders_to_process)} total tenders.")
    except Exception as e:
        log_error(f"Unexpected error in main function: {str(e)}")
        log_error(traceback.format_exc())
        raise
