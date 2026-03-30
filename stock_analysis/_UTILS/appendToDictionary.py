import os
from datetime import datetime

def push_tickers_todictionary(reporttype: str, all_tickers: dict, dictionaryfilename: str):
    """
    Generates a single, consolidated HTML report and prints the report details
    to the console.

    Args:
        all_tickers (dict): A dictionary where keys are the screener titles
                            and values are lists of stock ticker symbols.
    """
    # Define file path and name
    dictionary_output_dir = "E:/_scripts_PYTHON/_personal/_REPORT_Dictionary"
    
    today_date_str = datetime.now().strftime('%Y%m%d')
    
    dictionary_path = os.path.join(dictionary_output_dir, dictionaryfilename)
    
    # Ensure the directory exists
    os.makedirs(dictionary_output_dir, exist_ok=True)

    # Start writing the HTML report
    with open(dictionary_path, 'a') as f:
        
        ## #########################################################################
        ## Stock Screeners
        ## #########################################################################
        _subCategory_OverSold = "FINVIZ Stocker Screener - OverSold - Bounce Play"
        _line_subCategory_OverSold = "OverSold"
        
        _subCategory_ShortSqueeze = "FINVIZ Stocker Screener - ShortSqueeze"
        _line_subCategory_ShortSqueeze = "ShortSqueeze"
        
        _subCategory_BuyAndHold = "FINVIZ Stocker Screener - Buy and Hold"
        _line_subCategory_BuyAndHold = "BuyAndHold"
        
        #_subCategory_OffMovingAverages = "FINVIZ Stocker Screener - Off Moving Averages - Bounce Play"
        #_line_subCategory_OffMovingAverages = "OffMovingAverages"
        
        _subCategory_BreakOut = "FINVIZ Stocker Screener - BreakOut"
        _line_subCategory_BreakOut = "BreakOut"
        
        _subCategory_ChannelUp = "FINVIZ Stocker Screener - ChannelUp"
        _line_subCategory_ChannelUp = "ChannelUp"
        
        _subCategory_Volatility = "FINVIZ Stocker Screener - Volatility"
        _line_subCategory_Volatility = "Volatility"
        
        _subCategory_EarlyMomentum = "FINVIZ Stocker Screener - EarlyMomentum"
        _line_subCategory_EarlyMomentum = "EarlyMomentum"
        
        ## #########################################################################
        ## News Screeners
        ## #########################################################################
        _subCategory_Dividend = "FINVIZ News Stocker Screener - DIVIDEND"
        _line_subCategory_dividend = "DIVIDEND"
        
        _subCategory_STRATEGIC_PARTNERSHIP = "FINVIZ News Stocker Screener - STRATEGIC_PARTNERSHIP"
        _line_subCategory_STRATEGIC_PARTNERSHIP = "STRATEGIC_PARTNERSHIP"
        
        _subCategory_SECURITIES_PURCHASE = "FINVIZ News Stocker Screener - SECURITIES_PURCHASE"
        _line_subCategory_SECURITIES_PURCHASE = "SECURITIES_PURCHASE"
        
        _subCategory_ARTIFICIAL_INTELLIGENCE = "FINVIZ News Stocker Screener - ARTIFICIAL_INTELLIGENCE"
        _line_subCategory_ARTIFICIAL_INTELLIGENCE = "ARTIFICIAL_INTELLIGENCE"
        
        for subcategory, tickers in all_tickers.items():
            lineToBeAppended = today_date_str + ","
            lineCategory = ""
            
            if(subcategory == _subCategory_OverSold):
                lineCategory = "SCREENER"
                lineToBeAppended = lineToBeAppended + lineCategory + "," + _line_subCategory_OverSold + ","
            elif(subcategory == _subCategory_ShortSqueeze):
                lineCategory = "SCREENER"
                lineToBeAppended = lineToBeAppended + lineCategory + "," + _line_subCategory_ShortSqueeze + ","
            elif(subcategory == _subCategory_BuyAndHold):
                lineCategory = "SCREENER"
                lineToBeAppended = lineToBeAppended + lineCategory + "," + _line_subCategory_BuyAndHold + "," 
            elif(subcategory == _subCategory_BreakOut):
                lineCategory = "SCREENER"
                lineToBeAppended = lineToBeAppended + lineCategory + "," + _line_subCategory_BreakOut + "," 
            elif(subcategory == _subCategory_ChannelUp):
                lineCategory = "SCREENER"
                lineToBeAppended = lineToBeAppended + lineCategory + "," + _line_subCategory_ChannelUp + "," 
            elif(subcategory == _subCategory_Volatility):
                lineCategory = "SCREENER"
                lineToBeAppended = lineToBeAppended + lineCategory + "," + _line_subCategory_Volatility + "," 
            elif(subcategory == _subCategory_EarlyMomentum):
                lineCategory = "SCREENER"
                lineToBeAppended = lineToBeAppended + lineCategory + "," + _line_subCategory_EarlyMomentum + ","                 
            elif(subcategory == _subCategory_Dividend):
                lineCategory = "NEWS"
                lineToBeAppended = lineToBeAppended + lineCategory + "," + _line_subCategory_dividend + "," 
            elif(subcategory == _subCategory_STRATEGIC_PARTNERSHIP):
                lineCategory = "NEWS"
                lineToBeAppended = lineToBeAppended + lineCategory + "," + _line_subCategory_STRATEGIC_PARTNERSHIP + "," 
            elif(subcategory == _subCategory_SECURITIES_PURCHASE):
                lineCategory = "NEWS"
                lineToBeAppended = lineToBeAppended + lineCategory + "," + _line_subCategory_SECURITIES_PURCHASE + "," 
            elif(subcategory == _subCategory_ARTIFICIAL_INTELLIGENCE):
                lineCategory = "NEWS"
                lineToBeAppended = lineToBeAppended + lineCategory + "," + _line_subCategory_ARTIFICIAL_INTELLIGENCE + ","                 
            else:
                lineCategory = "UNRECOGNIZED"
                lineToBeAppended = lineToBeAppended + "UNRECOGNIZED" + "," + "UNRECOGNIZED" + "," 
                
            if not tickers:
                lineToBeAppended = lineToBeAppended + today_date_str + lineCategory
                f.write(lineToBeAppended + '\n')
                
                print(f">>  No tickers found for {lineCategory}-{subcategory}.")
                print(f">> ")
                continue

            # Concatenate tickers into a single, comma-separated string
            ticker_string = ",".join(tickers)
            
            # Construct the final file line
            lineToBeAppended = lineToBeAppended + ticker_string
            
            # Append to FileDictionary
            f.write(lineToBeAppended + '\n')

            # Print to console
            print(f">>  Tickers found for {lineCategory}-{subcategory}.")
            print(f">>  {ticker_string}")
            print(f">> ")

    print(f">> Stock Ticker Symbols saved to: {dictionary_path}")