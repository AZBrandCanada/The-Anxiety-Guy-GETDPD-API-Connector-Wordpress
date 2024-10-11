import requests
import json
import os

API_URL = 'https://api.getdpd.com/v2/purchases'
USERNAME = ''  # Replace with your username
PASSWORD = ''  # Replace with your API key/password
PAGE_FILE = 'current_page.txt'
DATA_FILE = 'transactions.txt'
PROCESSED_IDS_FILE = 'processed_ids.txt'

def get_current_page():
    """Retrieve the current page number from the file."""
    if os.path.exists(PAGE_FILE):
        with open(PAGE_FILE, 'r') as file:
            return int(file.read().strip())
    return 1

def save_current_page(page):
    """Save the current page number to a file."""
    with open(PAGE_FILE, 'w') as file:
        file.write(str(page))

def get_processed_ids():
    """Retrieve the set of processed purchase IDs from the file."""
    if os.path.exists(PROCESSED_IDS_FILE):
        with open(PROCESSED_IDS_FILE, 'r') as file:
            return set(line.strip() for line in file)
    return set()

def save_processed_id(purchase_id):
    """Save a processed purchase ID to the file."""
    with open(PROCESSED_IDS_FILE, 'a') as file:
        file.write(purchase_id + '\n')

def append_transactions(data):
    """Append new transactions to the data file."""
    processed_ids = get_processed_ids()
    with open(DATA_FILE, 'a') as file:
        for item in data:
            purchase_id = str(item.get('id'))
            if purchase_id in processed_ids:
                continue  # Skip already processed transactions

            for line_item in item.get('line_items', []):
                transaction = {
                    'product_name': line_item.get('product_name', 'Unknown'),
                    'email': item.get('buyer_email', 'Unknown')
                }
                file.write(json.dumps(transaction) + '\n')
            
            # Mark this purchase ID as processed
            save_processed_id(purchase_id)

def fetch_data(page):
    """Fetch data for a specific page."""
    try:
        response = requests.get(API_URL, auth=(USERNAME, PASSWORD), params={'page': page})
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx

        # Debug: Print raw response and parsed JSON
        print(f'Raw response for page {page}: {response.text}')

        data = response.json()
        print(f'Parsed JSON for page {page}: {data}')

        if isinstance(data, list) and len(data) > 0:
            return data
        
        # Handle cases where the response is not a list (e.g., error messages)
        if isinstance(data, dict) and data.get('status') == 'NOTFOUND':
            return None

        return data

    except requests.RequestException as e:
        print(f'Error fetching data for page {page}: {e}')
        return None

def main():
    """Main function to handle pagination and data retrieval."""
    current_page = get_current_page()

    while True:
        print(f'Fetching page {current_page}...')
        data = fetch_data(current_page)

        if data is None:
            print(f'No data found for page {current_page}.')
            break

        if isinstance(data, list) and len(data) > 0:
            append_transactions(data)
            save_current_page(current_page)
            current_page += 1
        else:
            print('No more data to fetch or error occurred.')
            break

if __name__ == '__main__':
    main()
