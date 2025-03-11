import requests
import pandas as pd
import os
import sys
import json
import traceback
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

    # Test API connectivity before starting the loop
    try:
        test_payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "system", "content": "Test message"}],
            "temperature": 0.3
        }
        response = requests.post(DEEPSEEK_API_URL, json=test_payload, timeout=5)
        if response.status_code != 200:
            log_error(f"API connectivity test failed with status {response.status_code}")
            write_debug_log(f"API connectivity test failed: {response.text}")
            raise ConnectionError(f"API connectivity test failed with status {response.status_code}")
        else:
            log_error("API connectivity test successful")
    except Exception as e:
        log_error(f"API connectivity test failed with exception: {str(e)}")
        write_debug_log(f"API connectivity test exception: {str(e)}")
        raise

    for tender in tenders:
        # Get tender ID
        tender_id = tender.get('id')
        
        # Find this tender in the full data
        tender_row = all_tender_data[all_tender_data['id'] == tender_id]
        
        if not tender_row.empty:
            # Get full description from the dataframe
            full_description = tender_row['Full Description'].iloc[0]
            tender_title = tender_row['title'].iloc[0]
        else:
            # Fallback to tender object if not found in CSV
            full_description = tender.get('description', "")
            tender_title = tender.get('title', "")
        
        # Prepare text for assessment
        tender_text = f"Title: {tender_title}\nDescription: {full_description}"

        # Construct prompt
        prompt = f"""
        A manufacturing plant has the following capabilities:
        {PLANT_CAPABILITIES}

        Based on this, determine if the following tender is RELEVANT to the plant. 
        Respond with exactly one word: RELEVANT or NOT RELEVANT.

        Tender details:
        {tender_text}
        """

        # DeepSeek API request
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "system", "content": "You analyze tenders for relevance."},
                         {"role": "user", "content": prompt}],
            "temperature": 0.3
        }

        write_debug_log(f"Processing tender ID: {tender_id} - {tender_title}")
        
        try:
            response = requests.post(DEEPSEEK_API_URL, json=payload, timeout=30)
            write_debug_log(f"API Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                write_debug_log(f"Raw AI response: '{ai_response}'")
                
                # More flexible matching - check if the response contains "RELEVANT"
                if "RELEVANT" in ai_response.upper() and "NOT RELEVANT" not in ai_response.upper():
                    write_debug_log(f"Tender {tender_id} marked as RELEVANT")
                    relevant_ids.append(tender_id)
                    relevant_tenders.append(tender)
                else:
                    write_debug_log(f"Tender {tender_id} marked as NOT RELEVANT")
            else:
                write_debug_log(f"Error: API returned status code {response.status_code}")
                write_debug_log(f"Response content: {response.text}")
                raise ConnectionError(f"API returned status code {response.status_code}")
        except Exception as e:
            write_debug_log(f"Exception when calling API: {str(e)}")
            log_error(f"Error processing tender {tender_id}: {e}")
            raise
    
    # Save filtered results
    if relevant_ids:
        filtered_data = all_tender_data[all_tender_data['id'].isin(relevant_ids)]
        filtered_tenders_path = resource_path("tender_data/filtered_tenders.csv")
        try:
            filtered_data.to_csv(filtered_tenders_path, index=False)
            log_error(f"Found {len(relevant_ids)} relevant tenders. Data saved to {filtered_tenders_path}")
            write_debug_log(f"CSV saved with {len(relevant_ids)} relevant tenders")
        except Exception as e:
            log_error(f"Error saving filtered tenders: {e}")
            write_debug_log(f"Error saving filtered tenders: {e}")
            raise
    else:
        log_error("No relevant tenders found.")
        write_debug_log("No relevant tenders found")
        
        # If no relevant tenders were found, create an empty filtered CSV
        filtered_tenders_path = resource_path("tender_data/filtered_tenders.csv")
        try:
            # Create a minimal version with required columns
            empty_df = pd.DataFrame(columns=all_tender_data.columns)
            empty_df.to_csv(filtered_tenders_path, index=False)
            write_debug_log("Created empty filtered CSV as no tenders matched")
        except Exception as e:
            log_error(f"Error creating empty filtered CSV: {e}")
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
