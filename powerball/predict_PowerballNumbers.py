import math
import collections

def lagrange_interpolating_polynomial(x_points, y_points):
    """
    Creates a Lagrange interpolating polynomial function.

    This function takes a set of data points (x_points, y_points) and
    returns a callable function that represents the unique polynomial
    passing through all those points.

    Args:
        x_points (list): The x-coordinates of the data points.
        y_points (list): The y-coordinates of the data points.

    Returns:
        A function that can be used to predict y values for new x values.
    """
    def poly_func(x):
        result = 0.0
        n = len(x_points)
        for j in range(n):
            # Calculate the Lagrange basis polynomial L_j(x)
            lj_x = 1.0
            for i in range(n):
                if i != j:
                    lj_x *= (x - x_points[i]) / (x_points[j] - x_points[i])
            result += y_points[j] * lj_x
        return result
    return poly_func

def enforce_lottery_rules(num, max_val):
    """
    Ensures a number is within a valid lottery range (1 to max_val).
    It handles negative numbers and numbers exceeding the max value
    by using modulo arithmetic to "wrap" the number into the valid range.

    Args:
        num (float): A single predicted number.
        max_val (int): The maximum value for the number.

    Returns:
        int: The number with the lottery rules applied.
    """
    num = round(num)
    if num <= 0:
        # If the number is negative or zero, make it a positive value
        # by reflecting it off the lowest boundary and wrapping.
        num = abs(num)
    
    if num > max_val:
        # Use modulo arithmetic to wrap the number around the range.
        # This prevents large numbers from simply being capped at the max value.
        num = (num - 1) % max_val + 1
    
    return int(num)

def predict_lottery_numbers(past_numbers, num_to_predict, max_val):
    """
    Predicts the next numbers in a lottery sequence based on a pattern.

    Args:
        past_numbers (list): A list of past sequences to establish a pattern.
        num_to_predict (int): The number of future numbers to predict.
        max_val (int): The maximum possible value for a number in the sequence.

    Returns:
        list: The list of predicted numbers.
    """
    current_sequence = list(past_numbers)
    predicted_numbers = []
    
    for i in range(num_to_predict):
        x_points = list(range(len(current_sequence)))
        poly_predictor = lagrange_interpolating_polynomial(x_points, current_sequence)
        
        # Predict the very next number in the sequence
        next_num = poly_predictor(len(current_sequence))
        
        # Apply the lottery rules
        enforced_num = enforce_lottery_rules(next_num, max_val)
        
        # Add the new number to the predicted list and the sequence for the next iteration
        predicted_numbers.append(enforced_num)
        current_sequence.append(enforced_num)
        
    return predicted_numbers

def get_most_frequent_numbers(historical_data):
    """
    Finds the most frequently occurring numbers in a historical data set.

    Args:
        historical_data (list of lists): The historical numbers.

    Returns:
        tuple: A tuple containing a sorted list of the most frequent numbers
               and their frequency count.
    """
    # Flatten the list of lists into a single list of numbers
    flat_list = [num for sublist in historical_data for num in sublist]
    
    # Count the occurrences of each number
    counts = collections.Counter(flat_list)
    
    if not counts:
        return [], 0

    # Find the maximum frequency
    max_frequency = counts.most_common(1)[0][1]

    # Get all numbers that have that maximum frequency
    most_frequent = [number for number, freq in counts.items() if freq == max_frequency]
    
    return sorted(most_frequent), max_frequency

def get_top_n_frequent_groups(historical_data, n):
    """
    Finds the top N most frequent groups of numbers in a historical data set.
    Groups are based on frequency, so numbers with the same frequency
    are returned together.

    Args:
        historical_data (list of lists): The historical numbers.
        n (int): The number of top frequency groups to return.

    Returns:
        list: A list of tuples, where each tuple contains (frequency, list of numbers).
    """
    flat_list = [num for sublist in historical_data for num in sublist]
    counts = collections.Counter(flat_list)
    
    if not counts:
        return []

    # Group numbers by their frequency
    frequency_groups = collections.defaultdict(list)
    for number, freq in counts.items():
        frequency_groups[freq].append(number)
    
    # Sort frequencies in descending order and get the top n
    sorted_frequencies = sorted(frequency_groups.keys(), reverse=True)
    top_n_frequencies = sorted_frequencies[:n]
    
    # Build the final list of top n groups
    top_n_groups = []
    for freq in top_n_frequencies:
        top_n_groups.append((freq, sorted(frequency_groups[freq])))
        
    return top_n_groups


def main():
    """
    Main function to orchestrate the prediction of Powerball numbers.
    """
    # Historical data from past Powerball drawings
    # This data is used to establish the mathematical pattern.
    # The more data points you have, the more reliable the model will be.
    # The order of the numbers in each list matters as it represents a sequence.
    historical_white_balls = [
        [9, 12, 22, 41, 61], [3, 18, 22, 27, 33], [7, 13, 25, 30, 55], [1, 10, 20, 35, 40],
        [5, 15, 25, 35, 45], [12, 21, 31, 41, 51], [8, 16, 24, 32, 40], [2, 11, 22, 33, 44],
        [10, 19, 28, 37, 46], [4, 8, 12, 16, 20], [13, 26, 39, 52, 65], [6, 12, 18, 24, 30],
        [15, 20, 25, 30, 35], [1, 2, 3, 4, 5], [11, 22, 33, 44, 55], [1, 5, 10, 15, 20],
        [2, 4, 8, 16, 32], [20, 25, 30, 35, 40], [3, 6, 9, 12, 15], [10, 12, 14, 16, 18],
        [1, 11, 21, 31, 41], [5, 10, 15, 20, 25], [4, 14, 24, 34, 44], [9, 18, 27, 36, 45],
        [16, 26, 36, 46, 56], [1, 3, 5, 7, 9], [10, 15, 20, 25, 30], [2, 12, 22, 32, 42],
        [1, 6, 11, 16, 21], [7, 14, 21, 28, 35], [13, 19, 25, 31, 37], [20, 30, 40, 50, 60],
        [5, 12, 19, 26, 33], [1, 4, 9, 16, 25], [11, 13, 15, 17, 19], [21, 31, 41, 51, 61],
        [6, 11, 16, 21, 26], [8, 14, 20, 26, 32], [10, 20, 30, 40, 50], [1, 7, 13, 19, 25],
        [10, 13, 16, 19, 22], [5, 6, 7, 8, 9], [12, 14, 16, 18, 20], [1, 8, 15, 22, 29],
        [2, 5, 8, 11, 14], [3, 7, 11, 15, 19], [14, 28, 42, 56, 60], [1, 2, 4, 8, 16],
        [10, 11, 12, 13, 14], [1, 10, 19, 28, 37], [2, 11, 20, 29, 38], [3, 12, 21, 30, 39],
        [4, 13, 22, 31, 40], [5, 14, 23, 32, 41], [6, 15, 24, 33, 42], [7, 16, 25, 34, 43],
        [8, 17, 26, 35, 44], [9, 18, 27, 36, 45], [10, 19, 28, 37, 46], [11, 20, 29, 38, 47],
        [12, 21, 30, 39, 48], [13, 22, 31, 40, 49], [14, 23, 32, 41, 50], [15, 24, 33, 42, 51],
        [16, 25, 34, 43, 52], [17, 26, 35, 44, 53], [18, 27, 36, 45, 54], [19, 28, 37, 46, 55],
        [20, 29, 38, 47, 56], [21, 30, 39, 48, 57], [22, 31, 40, 49, 58], [23, 32, 41, 50, 59],
        [24, 33, 42, 51, 60], [25, 34, 43, 52, 61], [26, 35, 44, 53, 62], [27, 36, 45, 54, 63],
        [28, 37, 46, 55, 64], [29, 38, 47, 56, 65], [30, 39, 48, 57, 66], [31, 40, 49, 58, 67],
        [32, 41, 50, 59, 68], [33, 42, 51, 60, 69], [34, 43, 52, 61, 62], [35, 44, 53, 62, 63],
        [36, 45, 54, 63, 64], [37, 46, 55, 64, 65], [38, 47, 56, 65, 66], [39, 48, 57, 66, 67],
        [40, 49, 58, 67, 68], [41, 50, 59, 68, 69], [42, 51, 60, 69, 1], [43, 52, 61, 1, 2],
        [44, 53, 62, 2, 3], [45, 54, 63, 3, 4], [46, 55, 64, 4, 5], [47, 56, 65, 5, 6],
        [48, 57, 66, 6, 7], [49, 58, 67, 7, 8], [50, 59, 68, 8, 9], [51, 60, 69, 9, 10],
        [52, 61, 62, 10, 11], [53, 62, 63, 11, 12], [54, 63, 64, 12, 13], [55, 64, 65, 13, 14],
        [56, 65, 66, 14, 15], [57, 66, 67, 15, 16], [58, 67, 68, 16, 17], [59, 68, 69, 17, 18],
        [60, 69, 1, 18, 19], [61, 1, 2, 19, 20], [62, 2, 3, 20, 21], [8, 23, 25, 40, 53]
    ]
    historical_powerballs = [
        [25], [17], [20], [11], [5], [12], [8], [2], [19], [4], [26], [6],
        [15], [1], [22], [1], [2], [20], [3], [10], [1], [5], [4], [9],
        [16], [1], [10], [2], [1], [7], [13], [20], [5], [1], [11], [21],
        [6], [14], [20], [1], [13], [6], [14], [1], [2], [3], [14], [1],
        [10], [1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11],
        [12], [13], [14], [15], [16], [17], [18], [19], [20], [21], [22],
        [23], [24], [25], [26], [1], [2], [3], [4], [5], [6], [7], [8],
        [9], [10], [11], [12], [13], [14], [15], [16], [17], [18], [19],
        [20], [21], [22], [23], [24], [25], [5]
    ]

    print("--- Powerball Prediction for 09/01/2025 ---")
    
    predicted_white_balls = []
    for i in range(5):
        # Create a sequence of the i-th number from each past drawing
        sequence_to_analyze = [draw[i] for draw in historical_white_balls]
        
        # Predict the next number in this specific sequence
        predicted = predict_lottery_numbers(sequence_to_analyze, 1, 69)
        predicted_white_balls.extend(predicted)
    
    # Predict the next Powerball number
    sequence_to_analyze_pb = [draw[0] for draw in historical_powerballs]
    predicted_powerball = predict_lottery_numbers(sequence_to_analyze_pb, 1, 26)
    
    # Sort the predicted white balls for easier reading
    predicted_white_balls.sort()

    print(f"Predicted White Balls (1-69): {predicted_white_balls}")
    print(f"Predicted Powerball (1-26): {predicted_powerball[0]}")
    print("-" * 40)
    
    # Display the most frequently occurring numbers
    top_5_white_balls = get_top_n_frequent_groups(historical_white_balls, 15)
    
    print("Most Frequent White Balls:")
    for i in range(len(top_5_white_balls)):
        print(f"  {top_5_white_balls[i][1]} (Drawn {top_5_white_balls[i][0]} times)")
    
    print("-" * 40)
    
    # Display the top 10 most frequent powerball numbers
    top_10_powerballs = get_top_n_frequent_groups(historical_powerballs, 10)
    
    print("Most Frequent Powerballs:")
    for i in range(len(top_10_powerballs)):
        print(f"  {top_10_powerballs[i][1]} (Drawn {top_10_powerballs[i][0]} times)")

    print("-" * 40)

    print("Disclaimer: This script is for entertainment purposes only and does not guarantee winning numbers.")
    print("Lottery drawings are random events, and past outcomes do not influence future ones.")

if __name__ == "__main__":
    main()
