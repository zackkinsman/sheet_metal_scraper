import requests
import pandas as pd
import os

# API details (update if needed)
DEEPSEEK_API_URL = "http://localhost:1234/v1/chat/completions"

# Model details
MODEL_NAME = "deepseek-r1-distill-qwen-7b"

# Load plant capabilities from a text file
capabilities_path = os.path.join(os.path.dirname(__file__), "..", "tender_data", "mulgrave_capabilities.txt")
with open(capabilities_path, "r") as f:
    PLANT_CAPABILITIES = f.read().strip()

def deepseek_filter(tenders):
    """
    Sends tenders to DeepSeek AI and filters out irrelevant ones.
    Returns a list of tenders deemed relevant.
    """
    relevant_tenders = []

    for tender in tenders:
        tender_text = f"Title: {tender['title']}\nDescription: {tender['description']}"

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

        response = requests.post(DEEPSEEK_API_URL, json=payload)

        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content'].strip().upper()

            if ai_response == "RELEVANT":
                with open("filtered_tenders.txt", "a") as file:
                    file.write(f"{tender['title']}\n{tender['description']}\n{ai_response}\n\n")
                relevant_tenders.append(tender)

    return relevant_tenders