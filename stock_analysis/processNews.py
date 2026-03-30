import sys
import os
from datetime import datetime
import csv

# Get the path to the 'utils' folder
screeners_path = os.path.join(os.path.dirname(__file__), '_Asset_SCREEN')
get_path = os.path.join(os.path.dirname(__file__), '_Asset_GET')
utils = os.path.join(os.path.dirname(__file__), '_UTILS')

# Add the folder to the system path so Python can find the module
sys.path.append(screeners_path)
sys.path.append(get_path)
sys.path.append(utils)

# Now you can import the script as a module
import extractTickers
import newsEvents
import generateScreenerReport
import appendToDictionary

def main():
    print(">>  BEGIN - PROCESSING - Stock News Screeners ...")
    
    # Get today's date in YYYYMMDD format
    today_date_str = datetime.now().strftime('%Y%m%d')

    screener_output_dir = "E:/_scripts_PYTHON/_personal/_INPUT"
    
    # #############################################################
    # 1 - Write to Console and Generate Report
    #   - Retrieve News Events Based Upon KeyWords
    
    dividend_category = "DIVIDEND"
    dividend_keywords = "special|cash|dividend|one-time|extraordinary"
    newsEvents.download_NewEvents(newscategory=dividend_category, keywords=dividend_keywords)
    
    # #############################################################
    # 2 - Write to Console and Generate Report
    #   - Retrieve News Events Based Upon KeyWords
    
    strategic_partnership_category = "STRATEGIC_PARTNERSHIP"
    
    dividend_keywords = "strategic|partnership|collaboration|MOU"
    newsEvents.download_NewEvents(newscategory=strategic_partnership_category, keywords=dividend_keywords) 
    
    # #############################################################
    # 3 - Write to Console and Generate Report
    #   - Retrieve News Events Based Upon KeyWords
    
    securities_purchase_category = "SECURITIES_PURCHASE"
    
    dividend_keywords = "securities|purchase|agreement"
    newsEvents.download_NewEvents(newscategory=securities_purchase_category, keywords=dividend_keywords) 
    
    # #############################################################
    # 4 - Write to Console and Generate Report
    #   - Retrieve News Events Based Upon KeyWords
    
    artificial_intelligence_category = "ARTIFICIAL_INTELLIGENCE"
    
    dividend_keywords = "accelerated|growth|artifical|intelligence"
    newsEvents.download_NewEvents(newscategory=artificial_intelligence_category, keywords=dividend_keywords)     

    # #############################################################
    # 5 - Write to Console and Generate Report
    #   - Retrieve News Events Based Upon KeyWords
    
    trump_category = "TRUMP"
    
    trump_keywords = "trump"
    newsEvents.download_NewEvents(newscategory=trump_category, keywords=trump_keywords)  
    
    # # #############################################################
    # # 5 - Extract Stock Ticker Symbols - From Output Files noted above
    # 
    # # ##########
    # #   - DIVIDEND
    # dividend_output_filename = f"{today_date_str}_{dividend_category}.csv"
    # dividend_output_dir_path = os.path.join(screener_output_dir, dividend_output_filename)
    # 
    # extractTickers.extract_stockticker_symbols(input_file_path=dividend_output_dir_path, output_dir=screener_output_dir)
    # 
    # # ##########
    # #   - STRATEGIC_PARTNERSHIP
    # strategic_partnership_output_filename = f"{today_date_str}_{strategic_partnership_category}.csv"
    # strategic_partnership_output_dir_path = os.path.join(screener_output_dir, strategic_partnership_output_filename)
    # 
    # extractTickers.extract_stockticker_symbols(input_file_path=strategic_partnership_output_dir_path, output_dir=screener_output_dir)
    # 
    # # ##########
    # #   - SECURITIES_PURCHASE
    # securities_purchase_output_filename = f"{today_date_str}_{securities_purchase_category}.csv"
    # securities_purchase_output_dir_path = os.path.join(screener_output_dir, securities_purchase_output_filename)
    # 
    # extractTickers.extract_stockticker_symbols(input_file_path=securities_purchase_output_dir_path, output_dir=screener_output_dir)
    # 
    # # ##########
    # #   - ARTIFICIAL_INTELLIGENCE
    # artificial_intelligence_output_filename = f"{today_date_str}_{artificial_intelligence_category}.csv"
    # artificial_intelligence_output_dir_path = os.path.join(screener_output_dir, artificial_intelligence_output_filename)
    # 
    # extractTickers.extract_stockticker_symbols(input_file_path=output_dir_path, output_dir=artificial_intelligence_output_dir_path)
    
    # #############################################################
    # 5 - Prepare Context for Report
    
    # # ##########
    # #   - DIVIDEND
    # output_file_name = f"{today_date_str}_{dividend_category}_TickerSymbols_Extracted.txt"
    # 
    # extracted_output_dir_path = os.path.join(screener_output_dir, output_file_name)
    # 
    # section_title = f"FINVIZ News Stocker Screener - {dividend_category}"
    # 
    # generateScreenerReport.processReport(reportsection=section_title, inputfilepath=extracted_output_dir_path)
    # 
    # # ##########
    # #   - STRATEGIC_PARTNERSHIP
    # output_file_name = f"{today_date_str}_{strategic_partnership_category}_TickerSymbols_Extracted.txt"
    # 
    # extracted_output_dir_path = os.path.join(screener_output_dir, output_file_name)
    # 
    # section_title = f"FINVIZ News Stocker Screener - {strategic_partnership_category}"
    # 
    # generateScreenerReport.processReport(reportsection=section_title, inputfilepath=extracted_output_dir_path)
    # 
    # # ##########
    # #   - SECURITIES_PURCHASE
    # output_file_name = f"{today_date_str}_{securities_purchase_category}_TickerSymbols_Extracted.txt"
    # 
    # extracted_output_dir_path = os.path.join(screener_output_dir, output_file_name)
    # 
    # section_title = f"FINVIZ News Stocker Screener - {securities_purchase_category}"
    # 
    # generateScreenerReport.processReport(reportsection=section_title, inputfilepath=extracted_output_dir_path)
    # 
    # # ##########
    # #   - ARTIFICIAL_INTELLIGENCE
    # output_file_name = f"{today_date_str}_{artificial_intelligence_category}_TickerSymbols_Extracted.txt"
    # 
    # extracted_output_dir_path = os.path.join(screener_output_dir, output_file_name)
    # 
    # section_title = f"FINVIZ News Stocker Screener - {artificial_intelligence_category}"
    # 
    # generateScreenerReport.processReport(reportsection=section_title, inputfilepath=extracted_output_dir_path)    
    
    dividend_section_title = f"FINVIZ News Stocker Screener - {dividend_category}"
    dividend_output_filename = f"{today_date_str}_{dividend_category}.csv" #20250911_DIVIDEND.csv
    
    strategic_partnership_section_title = f"FINVIZ News Stocker Screener - {strategic_partnership_category}"
    strategic_partnership_output_filename = f"{today_date_str}_{strategic_partnership_category}.csv"
    
    dsecurities_purchase_section_title = f"FINVIZ News Stocker Screener - {securities_purchase_category}"
    securities_purchase_output_filename = f"{today_date_str}_{securities_purchase_category}.csv"
    
    artificial_intelligence_section_title = f"FINVIZ News Stocker Screener - {artificial_intelligence_category}"
    dartificial_intelligence_output_filename = f"{today_date_str}_{artificial_intelligence_category}.csv"
    
    trump_section_title = f"FINVIZ News Stocker Screener - {trump_category}"
    trump_output_filename = f"{today_date_str}_{trump_category}.csv"
    
    all_screeners_data = {
        f"{dividend_section_title}": os.path.join(screener_output_dir, dividend_output_filename),
        f"{strategic_partnership_section_title}": os.path.join(screener_output_dir, strategic_partnership_output_filename),
        f"{dsecurities_purchase_section_title}": os.path.join(screener_output_dir, securities_purchase_output_filename),
        f"{artificial_intelligence_section_title}": os.path.join(screener_output_dir, dartificial_intelligence_output_filename),
        f"{trump_section_title}": os.path.join(screener_output_dir, trump_output_filename)
    }

    all_tickers = {}
    for section_title, file_path in all_screeners_data.items():
        tickers = []
        try:
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                # Skip the header row
                next(reader, None)
                for row in reader:
                    if row:
                        tickers.append(row[0].strip())
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An unexpected error occurred while processing '{file_path}': {e}")
        
        all_tickers[section_title] = tickers

    # #############################################################
    # 6 - Generate a single consolidated report
    reporttype = "News_Events"
    generateScreenerReport.process_consolidated_report(reporttype, all_tickers)
    
    appendToDictionary.push_tickers_todictionary(reporttype, all_tickers, "news_screener.dict")
    
    print(">>  ")
    print(">>  END - PROCESSING - Stock News Screeners ...")    

if __name__ == "__main__":
    main()