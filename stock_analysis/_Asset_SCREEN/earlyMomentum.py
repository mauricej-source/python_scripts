import os
import requests
from datetime import datetime

def download_EarlyMomentum(url: str, output_dir: str, output_filename: str = None) -> None:
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
        output_filename = f"{today_date_str}_EarlyMomentum.csv"

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