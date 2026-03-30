# ####################################################################################################
# - Original Approach
# ####################################################################################################
# import os
# import requests
# from datetime import datetime, timedelta, date
# 
# url = "https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=fa_debteq_0to1,fa_roe_o15,sh_avgvol_o100,sh_price_1to150,ta_change_u1,ta_highlow50d_nh,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=4&o=-price&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"
# 
# # Get today's date in YYYYMMDD format
# today_date_str = datetime.now().strftime('%Y%m%d')
# 
# output_dir = "E:/_scripts_PYTHON/_personal/_INPUT"
# 
# output_filename = f"{today_date_str}_BreakOut.csv"
# 
# output_dir_path = os.path.join(output_dir, output_filename)
# 
# response = requests.get(url)
# open(output_dir_path, "wb").write(response.content)

import os
import requests
from datetime import datetime

def download_BreakOut(url: str, output_dir: str, output_filename: str = None) -> None:
    """
    Downloads data from a given URL and saves it to a specified directory.

    Args:
        url (str): The URL of the data to download.
        output_dir (str): The directory to save the file.
        output_filename (str, optional): The name of the output file. 
                                         If None, a default name is generated.
    """
    
    if not output_filename:
        today_date_str = datetime.now().strftime('%Y%m%d')
        output_filename = f"{today_date_str}_BreakOut.csv"

    output_dir_path = os.path.join(output_dir, output_filename)

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        with open(output_dir_path, "wb") as f:
            f.write(response.content)
        print(f">>     Successfully downloaded and saved to\n>>     {output_dir_path}")
        print(f">>     ")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")