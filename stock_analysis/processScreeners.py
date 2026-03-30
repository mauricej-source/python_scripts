import time
import sys
import os
from datetime import datetime
import csv

# Get the path to the 'utils' folder
screeners_path = os.path.join(os.path.dirname(__file__), '_Asset_SCREEN')
get_path = os.path.join(os.path.dirname(__file__), '_Asset_GET')
utils = os.path.join(os.path.dirname(__file__), '_UTILS')

# Add the folders to the system path
sys.path.append(screeners_path)
sys.path.append(get_path)
sys.path.append(utils)

# Now you can import the script as a module
import lightningPlay
import oversoldBouncePlay
import shortSqueeze
import buyAndHold
import offMABouncePlay
import breakOut
import channelUp
import volatility
import earlyMomentum
import generateScreenerReport
import appendToDictionary

def main():
    print(">> BEGIN - PROCESSING - Stock Screeners...")

    # Get today's date in YYYYMMDD format
    today_date_str = datetime.now().strftime('%Y%m%d')

    screener_output_dir = "E:/_scripts_PYTHON/_personal/_INPUT"
    
    # Dictionaries to store both ticker and category for later report generation
    all_screeners_data = {}

    # #############################################################
    # 1 - Process Lightning Play
    url_LightningPlay = "https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=sh_price_u10,ta_perf_1wup,ta_perf2_dup,ta_rsi_42to70,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa,ta_volatility_wo2&ft=4&o=price&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"
    
    output_filename_LightningPlay = f"{today_date_str}_LightningPlay.csv"
    
    lightningPlay.download_LightningPlay(url=url_LightningPlay, output_dir=screener_output_dir, output_filename=output_filename_LightningPlay)
    
    # Add a delay of 1 to 5 seconds to avoid rate limiting
    time.sleep(3) 
    
    # #############################################################
    # 2 - Process OverSold - Bounce Play
    url_OversoldBouncePlay = "https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=sh_price_o3%2Csh_relvol_1to3%2Cta_change_1to100%2Cta_rsi_os30&ft=4&o=-change&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"
    output_filename_OversoldBouncePlay = f"{today_date_str}_OverSoldBouncePlay.csv"
    
    oversoldBouncePlay.download_OverSoldBouncePlay(url=url_OversoldBouncePlay, output_dir=screener_output_dir, output_filename=output_filename_OversoldBouncePlay)
    
    # Add a delay of 1 to 5 seconds to avoid rate limiting
    time.sleep(3) 
    
    # #############################################################
    # 3 - Process ShortSqueeze
    url_ShortSqueeze = "https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=an_recom_buybetter|holdbetter,sh_float_x40to100,sh_instown_10to100,sh_price_0.75to8.25,sh_short_o20,ta_change_u,ta_perf_1wup&ft=4&o=-price&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"
    output_filename_ShortSqueeze = f"{today_date_str}_ShortSqueeze.csv"
    
    shortSqueeze.download_ShortSqueeze(url=url_ShortSqueeze, output_dir=screener_output_dir, output_filename=output_filename_ShortSqueeze)
    
    # Add a delay of 1 to 5 seconds to avoid rate limiting
    time.sleep(3) 
    
    # #############################################################
    # 4 - Process Buy and Hold
    url_BuyAndHold = "https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=cap_microover,fa_curratio_o1.5,fa_eps5years_o10,fa_roe_o15,ta_beta_o1.5,ta_change_u,ta_sma20_pa&ft=4&o=-change&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"
    output_filename_BuyAndHold = f"{today_date_str}_BuyAndHold.csv"
    
    buyAndHold.download_BuyAndHold(url=url_BuyAndHold, output_dir=screener_output_dir, output_filename=output_filename_BuyAndHold)    
    
    # Add a delay of 1 to 5 seconds to avoid rate limiting
    time.sleep(3) 
    
    # #############################################################
    # 5 - Process Off Moving Averages - Bounce Play
    # url_OffMovingAveragesBouncePlay = "https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=sh_avgvol_o400%2Csh_curvol_o2000%2Csh_relvol_o1%2Cta_change_u2%2Cta_sma20_pa%2Cta_sma50_pb&ft=4&o=-change&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"
    # output_filename_OffMovingAveragesBouncePlay = f"{today_date_str}_OffMABouncePlay.csv"
    
    # offMABouncePlay.download_OffMovingAveragesBouncePlay(url=url_OffMovingAveragesBouncePlay, output_dir=screener_output_dir, output_filename=output_filename_OffMovingAveragesBouncePlay)
    
    # Add a delay of 1 to 5 seconds to avoid rate limiting
    # time.sleep(3) 
    
    # #############################################################
    # 6 - Process BreakOut
    url_BreakOut = "https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=sh_avgvol_o400%2Csh_curvol_o2000%2Csh_relvol_o1%2Cta_change_u2%2Cta_sma20_pa%2Cta_sma50_pb&ft=4&o=-change&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"    
    output_filename_BreakOut = f"{today_date_str}_BreakOut.csv"
    
    breakOut.download_BreakOut(url=url_BreakOut, output_dir=screener_output_dir, output_filename=output_filename_BreakOut)
    
    # Add a delay of 1 to 5 seconds to avoid rate limiting
    time.sleep(3) 
    
    # #############################################################
    # 7 - ChannelUp
    url_ChannelUp = "https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=sh_price_u40,sh_relvol_o1,ta_change_u1,ta_pattern_channelup,ta_perf_4wup,ta_perf2_1wup,ta_sma20_pa,ta_sma50_pa,ta_volatility_wo6&ft=4&o=-change&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"
    output_filename_ChannelUp = f"{today_date_str}_ChannelUp.csv"
    
    channelUp.download_ChannelUp(url=url_ChannelUp, output_dir=screener_output_dir, output_filename=output_filename_ChannelUp)

    # Add a delay of 1 to 5 seconds to avoid rate limiting
    time.sleep(3) 
    
    # #############################################################
    # 8 - Volatility
    url_Volatility = "https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=sh_opt_optionshort,sh_price_u10,ta_change_1to5,ta_volatility_8to20x5to8&ft=4&o=-change&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"
    output_filename_Volatility = f"{today_date_str}_Volatility.csv"
    
    volatility.download_Volatility(url=url_Volatility, output_dir=screener_output_dir, output_filename=output_filename_Volatility)
    
    # Add a delay of 1 to 5 seconds to avoid rate limiting
    time.sleep(3) 
    
    # #############################################################
    # 9 - Early Momentum
    url_EarlyMomentum = "https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=sec_technology|healthcare|industrials,sh_avgvol_o500,sh_curvol_o200,sh_relvol_o0.25,ta_change_u,ta_rsi_49to70,ta_sma20_pa,ta_sma50_pa,ta_volatility_wo15,tad_0_close::close:w|abveq:::|sma:50:sma:d&ft=4&o=-change&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"
    output_filename_EarlyMomentum = f"{today_date_str}_EarlyMomentum.csv"
    
    volatility.download_Volatility(url=url_EarlyMomentum, output_dir=screener_output_dir, output_filename=output_filename_EarlyMomentum)
    
    # Add a delay of 1 to 5 seconds to avoid rate limiting
    time.sleep(3) 
    
    # #############################################################
    # 10 - Prepare Context for Report
    
    all_screeners_data = {
        "FINVIZ Stocker Screener - Lightning Play": os.path.join(screener_output_dir, output_filename_LightningPlay),
        "FINVIZ Stocker Screener - OverSold - Bounce Play": os.path.join(screener_output_dir, output_filename_OversoldBouncePlay),
        "FINVIZ Stocker Screener - ShortSqueeze": os.path.join(screener_output_dir, output_filename_ShortSqueeze),
        "FINVIZ Stocker Screener - Buy and Hold": os.path.join(screener_output_dir, output_filename_BuyAndHold),
        # "FINVIZ Stocker Screener - Off Moving Averages - Bounce Play": os.path.join(screener_output_dir, output_filename_OffMovingAveragesBouncePlay),
        "FINVIZ Stocker Screener - BreakOut": os.path.join(screener_output_dir, output_filename_BreakOut),
        "FINVIZ Stocker Screener - ChannelUp": os.path.join(screener_output_dir, output_filename_ChannelUp),
        "FINVIZ Stocker Screener - Volatility": os.path.join(screener_output_dir, output_filename_Volatility),
        "FINVIZ Stocker Screener - EarlyMomentum": os.path.join(screener_output_dir, output_filename_EarlyMomentum)
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
    # 7 - Generate a single consolidated report
    reporttype = "Stock_Indicator"
    generateScreenerReport.process_consolidated_report(reporttype, all_tickers)
    
    appendToDictionary.push_tickers_todictionary(reporttype, all_tickers, "stock_screener.dict")
    
    print(">> ")
    print(">> END - PROCESSING - Stock Screeners...")

if __name__ == "__main__":
    main()