import requests
import pandas as pd
import os
import json

# API details (update if needed)
DEEPSEEK_API_URL = "http://localhost:1234/v1/chat/completions"

# Model details
MODEL_NAME = "deepseek-r1-distill-qwen-7b"

# Load plant capabilities from a text file
capabilities_path = os.path.join(os.path.dirname(__file__), "..", "tender_data", "mulgrave_capabilities.txt")
with open(capabilities_path, "r") as f:
    PLANT_CAPABILITIES = f.read().strip()

# Path to the tender data with descriptions CSV file
tender_descriptions_path = os.path.join(os.path.dirname(__file__), "..", "tender_data", "tender_data_with_descriptions.csv")

# Output file paths
filtered_tenders_path = os.path.join(os.path.dirname(__file__), "..", "tender_data", "filtered_tenders.csv")
debug_log_path = os.path.join(os.path.dirname(__file__), "..", "tender_data", "filter_debug.log")

def load_tender_data():
    """
    Load the tender data from the CSV file into a pandas DataFrame
    """
    try:
        df = pd.read_csv(tender_descriptions_path)
        return df
    except Exception as e:
        print(f"Error loading tender data: {e}")
        return pd.DataFrame()

def write_debug_log(message):
    """
    Write debug information to a log file
    """
    with open(debug_log_path, "a", encoding='utf-8') as f:
        f.write(f"{message}\n")

def deepseek_filter(tenders):
    """
    Sends tenders to DeepSeek AI and filters out irrelevant ones.
    Creates a CSV file with all relevant tenders and their full information.
    Returns a list of tenders deemed relevant.
    """
    relevant_tenders = []
    relevant_ids = []
    
    # Clear previous debug log
    with open(debug_log_path, "w", encoding='utf-8') as f:
        f.write("DeepSeek Filter Debug Log\n\n")
    
    # Load full tender data from CSV
    all_tender_data = load_tender_data()
    
    if all_tender_data.empty:
        print("Error: Could not load tender data with descriptions")
        return []
    
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
        except Exception as e:
            write_debug_log(f"Exception when calling API: {str(e)}")
            print(f"Error processing tender {tender_id}: {e}")
    
    # Create filtered CSV with all columns from the original data
    if relevant_ids:
        filtered_data = all_tender_data[all_tender_data['id'].isin(relevant_ids)]
        
        # Debug information about filtered data
        write_debug_log(f"\nRelevant tenders identified: {relevant_ids}")
        
        # Save as CSV
        filtered_data.to_csv(filtered_tenders_path, index=False)
        print(f"Found {len(relevant_ids)} relevant tenders. Data saved to {filtered_tenders_path}")
        write_debug_log(f"CSV saved with {len(relevant_ids)} relevant tenders")
    else:
        print("No relevant tenders found.")
        write_debug_log("No relevant tenders found")
    
    return relevant_tenders

# Standalone script functionality
if __name__ == "__main__":
    # Load all tenders from the CSV file
    all_tender_data = load_tender_data()
    
    if all_tender_data.empty:
        print("Error: Failed to load tender data")
    else:
        # Convert CSV data to the format expected by deepseek_filter
        tenders_to_process = []
        for _, row in all_tender_data.iterrows():
            tender = {
                'id': row['id'],
                'title': row['title'],
                'description': row.get('Full Description', '')
            }
            tenders_to_process.append(tender)
        
        print(f"Loaded {len(tenders_to_process)} tenders from CSV. Processing with AI filter...")
        
        # Filter tenders using DeepSeek AI
        relevant_tenders = deepseek_filter(tenders_to_process)
        
        # Print summary
        print(f"\nFinal results: {len(relevant_tenders)} relevant tenders identified out of {len(tenders_to_process)} total tenders.")
        print(f"Check {debug_log_path} for detailed processing information.")
