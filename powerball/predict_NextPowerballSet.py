def predict_next_set(historical_sets):
    """
    Analyzes a pattern in a series of number sets and predicts the final set.
    
    The pattern observed is that each second set is composed of multiples of a 
    base number. This base number is determined by adding a decreasing integer 
    (3, 2, 1, 0) to the starting number of the first set, which is always 8.

    Args:
        historical_sets (list of tuples): A list containing the historical sets. 
                                        The script's logic is based on the 
                                        order and structure of these sets.

    Returns:
        list: A list containing the predicted numbers for the final set.
    """
    
    # The pattern shows a decreasing sequence of integers added to 8.
    # The sequence is 3, 2, 1 for the historical data, so the next integer is 0.
    decreasing_integer = 0
    
    # The base number for the final set of multiples is 8 + 0 = 8.
    base_number = 8 + decreasing_integer
    
    # Generate the first five multiples of the base number.
    final_set = [base_number * i for i in range(1, 6)]
    
    return final_set

# Example input based on the provided historical data
sets = [
    ([8, 16, 24, 32, 40], [2, 11, 22, 33, 44]),
    ([8, 14, 20, 26, 32], [10, 20, 30, 40, 50]),
    ([8, 17, 26, 35, 44], [9, 18, 27, 36, 45]),
    ([8, 23, 25, 40, 53], [])  # The final set to be predicted
]

predicted_set = predict_next_set(sets)

# Print the final predicted set
print(f"The final predicted set is: {predicted_set}")