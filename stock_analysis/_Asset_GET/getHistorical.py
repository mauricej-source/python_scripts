import yfinance as yf
import pandas as pd
from datetime import datetime
import os

def download_historical_data(ticker, start_date, end_date, interval='1d', save_csv=True, filename=None):
    """
    Downloads historical data for a given ticker from Yahoo Finance.
    Saves the data to a CSV file in a dedicated './_OUTPUT' folder.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT', 'JNJ').
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        interval (str): Data interval (e.g., '1d' for daily, '1wk' for weekly, '1mo' for monthly).
        save_csv (bool): If True, saves the data to a CSV file.
        filename (str, optional): The name of the CSV file. If None, it defaults to
                                  '{ticker}_historical_data.csv'.

    Returns:
        pandas.DataFrame: A DataFrame containing the historical data.
    """
    # Define the output directory and ensure it exists
    output_folder = "./_OUTPUT"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")

    # Generate the filename with today's date prefix
    today_date_str = datetime.now().strftime('%Y%m%d')
    if filename is None:
        filename = f"{ticker}_historical_data.csv"
    
    # Construct the full file path
    full_filepath = os.path.join(output_folder, f"{today_date_str}_{filename}")

    try:
        print(f"Downloading historical data for {ticker} from {start_date} to {end_date} with interval {interval}...")
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)

        if data.empty:
            print(f"No data found for {ticker} within the specified range/interval.")
            return None

        if save_csv:
            data.to_csv(full_filepath)
            print(f"Data saved to {full_filepath}")
        else:
            print(f"Downloaded data for {ticker}:")
            print(data.head())
        
        return data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    # Example Usage:
    ticker_symbol = "JNJ"
    start = "2025-01-01"
    end = "2025-07-18"

    # Download daily data for JNJ and save to CSV
    jnj_data = download_historical_data(ticker_symbol, start, end)


    # You can find more information about JNJ historical data on these alternative sources:
    # - Johnson & Johnson - 63 Year Stock Price History: [https://www.macrotrends.net/stocks/charts/JNJ/johnson-johnson/stock-price-history](https://www.macrotrends.net/stocks/charts/JNJ/johnson-johnson/stock-price-history)
    # - Johnson & Johnson (JNJ) Stock Historical Price Data: [https://seekingalpha.com/symbol/JNJ/historical-price-quotes](https://seekingalpha.com/symbol/JNJ/historical-price-quotes)