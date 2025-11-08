import requests
from bs4 import BeautifulSoup
import csv
import time
import sys # For graceful error exit

# --- Configuration ---
BASE_URL = 'http://quotes.toscrape.com'
CSV_FILE_NAME = 'toscrape_quotes.csv'
HEADERS = {
    # Standard polite User-Agent header
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_page(url):
    """Fetches the HTML content of the target URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_data(html_content):
    """
    Parses the HTML and extracts the required data using selectors specific 
    to quotes.toscrape.com.
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    scraped_records = []

    # Selector for the container holding a single quote
    quote_containers = soup.select('div.quote') 
    
    # --- DEBUGGING LINE ---
    # Check how many quote containers were found. Should be 10 on most pages.
    print(f"DEBUG: Found {len(quote_containers)} quote containers on this page.")
    # ----------------------

    for container in quote_containers:
        try:
            # 1. Extract Quote Text (span with class 'text')
            quote_text_element = container.select_one('span.text')
            # Clean up smart quotes and strip whitespace
            quote_text = quote_text_element.text.strip().replace('“', '').replace('”', '') if quote_text_element else 'N/A'

            # 2. Extract Author Name (small with class 'author')
            author_element = container.select_one('small.author')
            author_name = author_element.text.strip() if author_element else 'N/A'
            
            # 3. Extract Tags (Find all 'a.tag' inside 'div.tags', then join them)
            tag_elements = container.select('div.tags a.tag') 
            tags = ', '.join([tag.text.strip() for tag in tag_elements])

            # Append the structured dictionary
            scraped_records.append({
                'Quote': quote_text,
                'Author': author_name,
                'Tags': tags
            })
            
        except Exception as e:
            # This catches issues with specific quote elements
            print(f"Error parsing a specific quote record: {e}")
            continue
            
    return scraped_records

def write_to_csv(data, filename):
    """Writes the list of dictionaries to a CSV file."""
    if not data:
        print("🛑 No data to write to CSV.")
        return

    # Use the keys of the first dictionary as dynamic column headers
    fieldnames = list(data[0].keys())
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data)
            
        print(f"✅ SUCCESS: Wrote {len(data)} total records to {filename}")
    except Exception as e:
        print(f"FATAL ERROR: Could not write to CSV file {filename}: {e}")
        sys.exit(1)


def main():
    """Main function to control the multi-page scraping process."""
    
    CURRENT_URL = BASE_URL
    all_extracted_data = [] # Stores data from ALL pages
    page_number = 1
    
    print(f"Starting scraping from: {BASE_URL}")
    
    # Loop continues as long as a valid URL is found for the next page
    while CURRENT_URL:
        print(f"\nProcessing Page {page_number}: {CURRENT_URL}")
        
        # 1. Fetch the HTML
        html_content = fetch_page(CURRENT_URL)
        
        if html_content:
            # 2. Parse the data
            extracted_data = parse_data(html_content)
            all_extracted_data.extend(extracted_data) # Add data to the master list
            
            # 3. Find the next page link (Pagination Logic)
            soup = BeautifulSoup(html_content, 'html.parser')
            # The 'Next' button is an 'a' tag inside an 'li' with class 'next'
            next_button = soup.select_one('li.next a') 
            
            if next_button and 'href' in next_button.attrs:
                # Construct the full URL for the next page
                CURRENT_URL = BASE_URL + next_button['href']
                page_number += 1
                # Polite delay before next request (2 seconds)
                time.sleep(2) 
            else:
                # No 'Next' button found, end the loop
                print("🛑 Reached the last page. Finalizing data.")
                CURRENT_URL = None 
        else:
            print("🚨 Fetching failed for this page. Stopping scraping.")
            CURRENT_URL = None

    # 4. Write all collected data to CSV after the loop finishes
    write_to_csv(all_extracted_data, CSV_FILE_NAME)

if __name__ == "__main__":
    main()