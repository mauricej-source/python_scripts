import pandas as pd
import os
import csv
import sys
from typing import List
from datetime import datetime, timedelta, date

def extract_stockticker_symbols(input_file_path: str, output_dir: str, output_filename: str = None) -> None:
    """
    Reads a CSV file, extracts the Ticker column, and saves it
    to a new comma-delimited text file in a specified directory.
    The output filename is based on the input filename.

    Args:
        input_file_path (str): The path to the input CSV file.
        output_dir (str): The directory to save the file.
        output_filename (str, optional): The name of the output file. 
                                         If None, a default name is generated.
    """
    # Check if the input file exists
    if not os.path.exists(input_file_path):
        print(f"Error: The file '{input_file_path}' was not found.")
        sys.exit(1)
        
    # Check if the output directory exists, and create it if it doesn't
    if not os.path.exists(output_dir):
        print(f">>     Creating output directory: {output_dir}")
        os.makedirs(output_dir)

    try:
        # Construct the output filename
        base_name = os.path.basename(input_file_path)
        file_name_without_ext = os.path.splitext(base_name)[0]
        
        if not output_filename:
            output_file_name = f"{file_name_without_ext}_TickerSymbols_Extracted.txt"
        
        # Combine the directory and filename to create the full output path
        output_path = os.path.join(output_dir, output_file_name)

        # Read the input file line by line
        with open(input_file_path, 'r') as f:
            lines = f.readlines()

        # Extract tickers and remove any double quotes
        tickers = [line.strip().split(',')[0].replace('"', '') for line in lines[1:]]

        # Join the list of tickers with a comma and write to the output file
        with open(output_path, 'w') as f:
            f.write(",".join(tickers))
        
        print(f">>     ##########")
        print(f">>     Tickers successfully extracted and saved to \n>>     '{output_path}'.")
        print(f">>     ")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

# ####################################################################################################
# - Original Approach
# ####################################################################################################
# if __name__ == "__main__":
#     # The script can be run from the command line with two arguments:
#     # 1. The name of the input CSV file
# 
#     if len(sys.argv) != 2:
#         print("Usage: python extract_tickers.py <input_file.csv>")
#         sys.exit(1)
# 
#     # Example
#     # E:/_scripts_PYTHON/_personal/_INPUT/20250910_shortSqueeze.csv
#     input_file = sys.argv[1]
#     
#     # Get today's date in YYYYMMDD format
#     today_date_str = datetime.now().strftime('%Y%m%d')
# 
#     output_dir = "E:/_scripts_PYTHON/_personal/_INPUT"
# 
#     output_filename = f"{today_date_str}_GetTickers.txt"
# 
#     output_dir_path = os.path.join(output_dir, output_filename)
#     
#     extract_tickers(input_file, output_dir_path)
