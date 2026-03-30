import csv
import argparse
import os

def find_tickers_in_price_range(input_csv_file, output_csv_file, min_price, max_price):
    """
    Finds stock ticker symbols within a specified price range from a CSV file
    and writes them to a new CSV file as a single, comma-separated row.

    Args:
        input_csv_file (str): The path to the input CSV file.
        output_csv_file (str): The path to the output CSV file.
        min_price (float): The minimum closing price for filtering.
        max_price (float): The maximum closing price for filtering.
    """
    found_tickers = set()  # Use a set to store unique tickers

    try:
        # Check if the input file exists
        if not os.path.exists(input_csv_file):
            print(f"Error: The input CSV file '{input_csv_file}' was not found.")
            return

        with open(input_csv_file, mode='r', newline='') as infile:
            reader = csv.DictReader(infile)
            fieldnames = [name.lower() for name in reader.fieldnames]

            if not all(col in fieldnames for col in ['ticker', 'close']):
                print(f"Error: The CSV file '{input_csv_file}' must contain 'ticker' and 'close' columns (case-insensitive).")
                return

            for row in reader:
                try:
                    close_price = float(row['close'])
                    if min_price <= close_price <= max_price:
                        found_tickers.add(row['ticker'])
                except ValueError:
                    print(f"Warning: Could not convert 'close' price '{row['close']}' to a number for ticker '{row['ticker']}'. Skipping.")
                except KeyError:
                    print(f"Warning: 'close' column not found in row: {row}. Skipping.")

        with open(output_csv_file, mode='w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['Filtered Tickers'])  # Write a single header row
            if found_tickers:
                sorted_tickers = sorted(list(found_tickers))
                writer.writerow(sorted_tickers)
                print(f"Found {len(found_tickers)} tickers between ${min_price:.2f} and ${max_price:.2f}.")
                print(f"Results saved to '{output_csv_file}' in a single comma-delimited row.")
            else:
                writer.writerow(['No tickers found in the specified price range.'])
                print(f"No tickers found between ${min_price:.2f} and ${max_price:.2f}.")
                print(f"An empty or warning message has been written to '{output_csv_file}'.")

    except FileNotFoundError:
        # This is redundant with the initial check but kept for robustness
        print(f"Error: The file '{input_csv_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Define a custom usage message to make it clearer for the user
    parser = argparse.ArgumentParser(
        description="Filters stock tickers from a CSV file by their closing price.",
        epilog="Example: python ticker_filter.py my_data.csv"
    )

    # The CSV file path is a required positional argument
    parser.add_argument(
        'csv_file',
        type=str,
        help='The path to the input CSV file (e.g., OTCBB_20250828.csv).'
    )
    
    # We add arguments for min and max price with default values
    parser.add_argument(
        '--min',
        dest='min_price',
        type=float,
        default=0.22,
        help='The minimum closing price for filtering. Defaults to $0.22.'
    )
    
    parser.add_argument(
        '--max',
        dest='max_price',
        type=float,
        default=0.55,
        help='The maximum closing price for filtering. Defaults to $0.55.'
    )

    # Parse the command-line arguments. The -h and --help flags are handled automatically.
    args = parser.parse_args()

    # Define the output directory
    output_dir = "./_OUTPUT"
    
    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate the output filename based on the input filename
    base_name = os.path.basename(args.csv_file)
    file_name_without_ext, ext = os.path.splitext(base_name)
    output_filename = f"{file_name_without_ext}_filtered.csv"
    
    # Combine the directory and the filename
    output_file = os.path.join(output_dir, output_filename)

    # Call the main function with the parsed arguments and the new output filename
    find_tickers_in_price_range(
        args.csv_file,
        output_file,
        args.min_price,
        args.max_price
    )
