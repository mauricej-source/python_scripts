import os
import requests
from datetime import datetime

def download_NewEvents(newscategory: str, keywords: str) -> None:
    """
    Downloads data from a given URL and saves it to a specified directory.

    Args:
        newscategory (str): leveraged in the filename convention
        keywords (str): Integrated within the URL to act as a basis for the News Search
    """
    today_date_str = datetime.now().strftime('%Y%m%d')
        
    if not newscategory:
        newscategory = "NEWS_Screener"

    output_dir = "E:/_scripts_PYTHON/_personal/_INPUT"
    output_filename = f"{today_date_str}_{newscategory}.csv"
    output_dir_path = os.path.join(output_dir, output_filename)

    url = f"https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=news_date_today|sinceyesterday|yesterday|todayafter|prevdays7|prevhours1|prevminutes5|prevhours24|prevminutes30|yesterdayafter|sinceyesterdayafter,news_keywords_{keywords},sh_price_0.75to65,ta_change_u&ft=4&o=-change&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"  
    
    # Example of Keywords Format
    # special|cash|dividend|one-time|extraordinary
    
    if not keywords:
        print(f"Error: The Keywords was not found.")
        sys.exit(1)
            
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        with open(output_dir_path, "wb") as f:
            f.write(response.content)
        print(f">>     Successfully downloaded and saved News Events to\n>>     {output_dir_path}")
        print(f">>     ")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")