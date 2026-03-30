import csv
from collections import Counter, defaultdict
import os
from datetime import datetime, timedelta

def find_frequent_ticker_subcategory_counts_grouped(filename="stock_screener.dict"):
    """
    Reads a file, filters rows by date (last 45 days), processes data, 
    and generates an HTML table with two sections: a new table showing tickers 
    in multiple subcategories, followed by the main subcategory-grouped table.
    """
    # 1. Test if the file exists
    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found. Cannot proceed.")
        return

    # --- Date Range Calculation ---
    current_date = datetime.now().date()
    past_cutoff_date = current_date - timedelta(days=45)
    current_date_str = current_date.strftime("%Y%m%d")
    past_cutoff_date_str = past_cutoff_date.strftime("%Y%m%d")

    print(f"Filtering data between {past_cutoff_date_str} and {current_date_str} (Last 45 Days).")
    
    # --- Data Processing & Initial Filtering (Count >= 3) ---
    ticker_subcategory_pairs = []
    try:
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)
            try:
                next(reader) # Skip header
            except StopIteration:
                print(f"File '{filename}' is empty.")
                return

            for row in reader:
                if len(row) >= 4:
                    file_date_str = row[0].strip()
                    if file_date_str >= past_cutoff_date_str and file_date_str <= current_date_str:
                        subcategory = row[2].strip()
                        tickers_in_row = [ticker.strip() for ticker in row[3:] if ticker.strip()]

                        for ticker in tickers_in_row:
                            ticker_subcategory_pairs.append((ticker, subcategory))
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    # --- Count and Final Filter (frequent_pairs list) ---
    pair_counts = Counter(ticker_subcategory_pairs)
    frequent_pairs = []
    
    # Data structures for the NEW Diverse Tickers table calculation
    ticker_diversity_set = defaultdict(set) # For counting unique subcategories
    total_ticker_occurrence = defaultdict(int)
    ticker_subcat_details = defaultdict(list) # NEW: To store (Subcategory, Occurrence) details

    for (ticker, subcategory), count in pair_counts.items():
        if count >= 3: 
            item = {'Ticker': ticker, 'SubCategory': subcategory, 'Occurrences': count}
            frequent_pairs.append(item)
            
            # Populate data for the NEW table
            ticker_diversity_set[ticker].add(subcategory)
            total_ticker_occurrence[ticker] += count
            ticker_subcat_details[ticker].append({'SubCategory': subcategory, 'Occurrences': count})
    
    if not frequent_pairs:
        print("\nNo unique Ticker/SubCategory combinations were found with 3 or more occurrences in the specified date range. No output generated.")
        return

    # --------------------------------------------------------------------
    # --- 1. PROCESS DATA FOR NEW DIVERSE TICKERS TABLE ---
    # --------------------------------------------------------------------
    diverse_tickers = []
    for ticker, subcats in ticker_diversity_set.items():
        if len(subcats) > 1:
            # Sort the subcategory details by Occurrence (Descending)
            subcat_details = sorted(
                ticker_subcat_details[ticker], 
                key=lambda x: x['Occurrences'], 
                reverse=True
            )
            
            diverse_tickers.append({
                'Ticker': ticker,
                'TotalOccurrences': total_ticker_occurrence[ticker],
                'Subcategories': subcat_details # Contains the detailed list
            })

    # 2. Sort New Table: Ticker (A-Z), then Total Occurrences (Descending)
    diverse_tickers.sort(key=lambda x: (x['Ticker'], -x['TotalOccurrences']))

    # --------------------------------------------------------------------
    # --- 2. PROCESS DATA FOR ORIGINAL SUBCATEGORY TABLE (Sorting) ---
    # --------------------------------------------------------------------
    # Sorting: Group by SubCategory, then sort by Occurrence Count (Descending)
    frequent_pairs.sort(key=lambda item: (
        item['SubCategory'],                      # 1. Group by SubCategory (Alphabetical A-Z)
        -item['Occurrences'],                     # 2. Sort by Occurrence Count (Descending)
        item['Ticker']                            # 3. Sort by Ticker (Alphabetical A-Z, as tie-breaker)
    ))

    # ----------------------------------------------------
    # --- Console Output (Main Table) ---
    # ----------------------------------------------------
    print("\n--- Stock Tickers (Grouped by SubCategory) with 3 or More Occurrences ---\n")

    TICKER_WIDTH = 10
    SUBCAT_WIDTH = 25
    COUNT_WIDTH = 15
    TOTAL_WIDTH = TICKER_WIDTH + SUBCAT_WIDTH + COUNT_WIDTH

    print(f"{'Ticker':<{TICKER_WIDTH}}{'SubCategory':<{SUBCAT_WIDTH}}{'Occurrences':<{COUNT_WIDTH}}")
    print("-" * TOTAL_WIDTH)

    current_group_key = None
    for item in frequent_pairs:
        if item['SubCategory'] != current_group_key and current_group_key is not None:
            print("=" * TOTAL_WIDTH) 
        
        print(f"{item['Ticker']:<{TICKER_WIDTH}}{item['SubCategory']:<{SUBCAT_WIDTH}}{item['Occurrences']:<{COUNT_WIDTH}}")
        current_group_key = item['SubCategory']
    
    print("-" * TOTAL_WIDTH)


    # ----------------------------------------------------
    # --- HTML Generation ---
    # ----------------------------------------------------

    # Extract unique tickers for the consolidated screener link
    unique_tickers = sorted(list(set(item['Ticker'] for item in frequent_pairs)))
    ticker_screener_list = ",".join(unique_tickers)
    BASE_SCREENER_URL = "https://elite.finviz.com/screener.ashx?v=111&t="
    screener_url = f"{BASE_SCREENER_URL}{ticker_screener_list}"
    screener_link_html = f'<p><strong>Consolidated Screener:</strong> <a href="{screener_url}" target="_blank">View All {len(unique_tickers)} Tickers on FinViz</a></p>'


    # HTML file details
    current_date_prefix = datetime.now().strftime("%Y%m%d")
    html_filename = f"{current_date_prefix}_MostFrequent_Stocks_Screened.html"
    BASE_FINVIZ_URL = "https://elite.finviz.com/quote.ashx?t="

    html_content = []
    html_content.append("<!DOCTYPE html>")
    html_content.append("<html lang='en'>")
    html_content.append("<head>")
    html_content.append("    <meta charset='UTF-8'>")
    html_content.append(f"    <title>Most Frequent Tickers by News SubCategory ({past_cutoff_date_str} to {current_date_str})</title>")
    html_content.append("    <style>")
    html_content.append("        body { font-family: Arial, sans-serif; margin: 20px; }")
    html_content.append("        h1 { color: #333; }")
    html_content.append("        table { width: 65%; border-collapse: collapse; margin-top: 20px; }") # Increased width for new table
    html_content.append("        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; }")
    html_content.append("        th { background-color: #f2f2f2; }")
    html_content.append("        tr.group-separator td { border-top: 3px solid #000; background-color: #f0f0f0; height: 5px; padding: 0; }")
    html_content.append("        .main-report td:nth-child(3) { text-align: center; }") # Center Occurrences for main table
    html_content.append("        .diverse-table td:nth-child(2), .diverse-table td:nth-child(3) { text-align: center; }") # Center Occurrences/Diversity for new table
    html_content.append("        .diverse-table ul { list-style-type: none; padding: 0; margin: 0; }") # Clean up list in diversity column
    html_content.append("    </style>")
    html_content.append("</head>")
    html_content.append("<body>")
    html_content.append(f"<h1>Most Frequent Tickers by SubCategory</h1>")
    html_content.append(f"<h3>Data Filtered: {past_cutoff_date_str} to {current_date_str}</h3>")
    
    # Insert the consolidated screener link
    html_content.append(screener_link_html) 
    

    # ----------------------------------------------------
    # --- NEW: DIVERSE TICKERS TABLE ---
    # ----------------------------------------------------
    if diverse_tickers:
        html_content.append("<h2>Tickers Occurring in Multiple Subcategories ($\ge$ 3 Occurrences each)</h2>")
        html_content.append('<table class="diverse-table">')
        html_content.append("    <thead>")
        html_content.append("        <tr>")
        html_content.append("            <th>Ticker</th>")
        html_content.append("            <th>Total Occurrences</th>")
        html_content.append("            <th>Subcategory Diversity (Subcategory: Count)</th>") # Updated Column Header
        html_content.append("        </tr>")
        html_content.append("    </thead>")
        html_content.append("    <tbody>")
        
        for item in diverse_tickers:
            ticker = item['Ticker']
            # FinViz quote link for individual tickers
            ticker_link = f'<a href="{BASE_FINVIZ_URL}{ticker}" target="_blank">{ticker}</a>'
            
            # Build the Subcategory Diversity list
            subcat_list_html = "<ul>"
            for subcat_detail in item['Subcategories']:
                subcat_list_html += f"<li>{subcat_detail['SubCategory']} ({subcat_detail['Occurrences']})</li>"
            subcat_list_html += "</ul>"
            
            html_content.append("        <tr>")
            html_content.append(f"            <td>{ticker_link}</td>")
            html_content.append(f"            <td>{item['TotalOccurrences']}</td>")
            html_content.append(f"            <td>{subcat_list_html}</td>") # Insert the list HTML
            html_content.append("        </tr>")
            
        html_content.append("    </tbody>")
        html_content.append("</table>")
        html_content.append("<hr>") # Separator line
    else:
        html_content.append("<p>No Tickers were found to occur in multiple subcategories ($\ge 3$ occurrences each) within the last 45 days.</p>")


    # ----------------------------------------------------
    # --- ORIGINAL SUBCATEGORY-GROUPED TABLE ---
    # ----------------------------------------------------
    html_content.append("<h2>Main Report: Grouped by Subcategory (Occurrences $\ge$ 3)</h2>")
    html_content.append('<table class="main-report">')
    
    # Table Header
    html_content.append("    <thead>")
    html_content.append("        <tr>")
    html_content.append("            <th>Ticker</th>")
    html_content.append("            <th>SubCategory</th>")
    html_content.append("            <th>Occurrences</th>")
    html_content.append("        </tr>")
    html_content.append("    </thead>")
    html_content.append("    <tbody>")

    # Table Data
    current_group_key = None
    for item in frequent_pairs:
        # Add a separator row before a new group starts (Subcategory group)
        if item['SubCategory'] != current_group_key and current_group_key is not None:
            html_content.append("        <tr class='group-separator'><td colspan='3'></td></tr>")
        
        ticker = item['Ticker']
        ticker_link = f'<a href="{BASE_FINVIZ_URL}{ticker}" target="_blank">{ticker}</a>'
        
        html_content.append("        <tr>")
        html_content.append(f"            <td>{ticker_link}</td>")
        html_content.append(f"            <td>{item['SubCategory']}</td>")
        html_content.append(f"            <td style='text-align: center;'>{item['Occurrences']}</td>")
        html_content.append("        </tr>")
        current_group_key = item['SubCategory']
        
    html_content.append("    </tbody>")
    html_content.append("</table>")
    html_content.append("</body>")
    html_content.append("</html>")

    # Write the content to the file
    try:
        with open(html_filename, 'w') as f:
            f.write('\n'.join(html_content))
        print(f"\n✅ Successfully generated HTML file: {html_filename}")
    except Exception as e:
        print(f"An error occurred while writing the HTML file: {e}")

# Execute the function
find_frequent_ticker_subcategory_counts_grouped()