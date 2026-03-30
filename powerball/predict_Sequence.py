def find_pattern(sequence):
    """
    Analyzes a sequence to find a mathematical pattern.

    Args:
        sequence (list): A list of numbers.

    Returns:
        dict: A dictionary containing the pattern type and relevant data.
    """
    if len(sequence) < 2:
        return {"type": "Too Short"}

    # Check for Arithmetic Sequence
    diffs = [sequence[i+1] - sequence[i] for i in range(len(sequence) - 1)]
    if len(set(diffs)) == 1:
        return {"type": "Arithmetic", "difference": diffs[0]}

    # Check for Geometric Sequence
    if sequence[0] != 0 and all(n != 0 for n in sequence[1:]):
        ratios = [sequence[i+1] / sequence[i] for i in range(len(sequence) - 1)]
        if len(set(ratios)) == 1:
            return {"type": "Geometric", "ratio": ratios[0]}

    # Check for Polynomial Sequence
    def find_polynomial_degree(seq):
        if len(seq) < 2:
            return None, []

        diff_seqs = [seq]
        while len(diff_seqs[-1]) > 1:
            next_diff_seq = [diff_seqs[-1][i+1] - diff_seqs[-1][i] for i in range(len(diff_seqs[-1]) - 1)]
            diff_seqs.append(next_diff_seq)
            if len(set(next_diff_seq)) == 1:
                return len(diff_seqs) - 1, [s[0] for s in diff_seqs[1:]]
        return None, []

    degree, diff_list = find_polynomial_degree(sequence)
    if degree is not None:
        return {"type": "Polynomial", "degree": degree, "diffs": diff_list}

    return {"type": "None"}

def lagrange_interpolating_polynomial(x_points, y_points):
    """
    Creates a Lagrange interpolating polynomial function.
    
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

def enforce_number_rules(num):
    """
    Ensures a number is positive and does not exceed 69.
    
    Args:
        num (float): A single number.
    
    Returns:
        int: The number with the rules applied.
    """
    # Rule 1: Make number positive
    if num <= 0:
        num *= -1 if num < 0 else 1
    
    # Rule 2: Ensure number does not exceed 69
    if num > 69:
        num = (num - 1) % 69 + 1
    
    return round(num)

def analyze_and_predict(source_date, source_numbers, target_date, target_numbers):
    """
    Analyzes the predictive relationship between two series.
    
    Args:
        source_date (str): The date of the source series.
        source_numbers (list): The numbers from the source series.
        target_date (str): The date of the target series.
        target_numbers (list): The numbers from the target series.
    """
    if len(source_numbers) != len(target_numbers):
        print(f"Prediction from {source_date} to {target_date} failed: The series have different lengths.")
        print("-" * 30)
        return

    # Calculate the differences between the two series
    diff_sequence = [target_numbers[i] - source_numbers[i] for i in range(len(target_numbers))]
    
    # Define the x-points for the polynomials
    x_points = list(range(len(source_numbers)))
    
    # Create the polynomial function for the source series
    poly_source_predictor = lagrange_interpolating_polynomial(x_points, source_numbers)
    
    # Create the polynomial function for the difference sequence
    poly_diff_predictor = lagrange_interpolating_polynomial(x_points, diff_sequence)

    # Use the combined polynomials to predict the target series from the source
    predicted_target = []
    for i in x_points:
        predicted_source = poly_source_predictor(i)
        predicted_diff = poly_diff_predictor(i)
        predicted_target.append(enforce_number_rules(predicted_source + predicted_diff))

    print(f"--- Predicting {target_date} from {source_date} ---")
    print(f"Original numbers from {target_date}: {target_numbers}")
    print(f"Predicted numbers: {predicted_target}")
    
    if target_numbers == predicted_target:
        print("The prediction was a perfect match!")
    else:
        print("The prediction did not match. This suggests a more complex relationship or insufficient data.")

    print("-" * 30)

def predict_next_numbers(sequence, num_predictions):
    """
    Predicts the next numbers in a sequence, handling capping and resetting iteratively.
    
    Args:
        sequence (list): The initial sequence of numbers.
        num_predictions (int): The number of future numbers to predict.
    
    Returns:
        list: The list of predicted numbers with capping and resetting applied.
    """
    current_sequence = list(sequence)
    predicted_numbers = []
    
    for _ in range(num_predictions):
        x_points = list(range(len(current_sequence)))
        poly_predictor = lagrange_interpolating_polynomial(x_points, current_sequence)
        
        # Predict the very next number
        next_num = poly_predictor(len(current_sequence))
        
        # Apply the capping and reset logic
        capped_num = enforce_number_rules(next_num)
        
        # Add the capped number to our predicted list and the sequence for the next iteration
        predicted_numbers.append(capped_num)
        current_sequence.append(capped_num)
        
    return predicted_numbers

def main():
    """
    Main function to analyze and predict numbers from one series to another.
    """
    series_w_date = "08/23/2025"
    series_w_numbers = [11, 14, 34, 47, 51]

    series_x_date = "08/25/2025"
    series_x_numbers = [16, 19, 34, 37, 64]

    series_y_date = "08/27/2025"
    series_y_numbers = [9, 12, 22, 41, 61]
    
    # series_z_date = "08/30/2025"
    # series_z_numbers = [3, 18, 22, 27, 33]
    
    # Predict series X from series W
    analyze_and_predict(series_w_date, series_w_numbers, series_x_date, series_x_numbers)
    
    # Predict series Y from series X
    analyze_and_predict(series_x_date, series_x_numbers, series_y_date, series_y_numbers)
    
    # Predict series Z from series Y
    # analyze_and_predict(series_y_date, series_y_numbers, series_z_date, series_z_numbers)
    
    # Predict next 5 numbers for 09/01/2025
    predicted_next_sequence = predict_next_numbers(series_y_numbers, 5)
    print("--- Prediction for 09/01/2025 ---")
    print(f"Predicted numbers: {predicted_next_sequence}")

if __name__ == "__main__":
    main()
