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

def analyze_relationship(series_a, series_b):
    """
    Analyzes the relationship between two series by finding the pattern in their differences.
    
    Args:
        series_a (list): The target series (e.g., the later date).
        series_b (list): The reference series (e.g., the earlier date).
    
    Returns:
        None
    """
    if len(series_a) != len(series_b):
        print("Cannot find a direct relationship: The series have different lengths.")
        return

    diff_sequence = [series_a[i] - series_b[i] for i in range(len(series_a))]
    print(f"The differences between the two series (A - B) are: {diff_sequence}")
    
    pattern_in_diffs = find_pattern(diff_sequence)
    print(f"The pattern found in these differences is: {pattern_in_diffs['type']}")
    
    if pattern_in_diffs['type'] == 'Arithmetic':
        print(f"You can predict numbers in Series A by adding {pattern_in_diffs['difference']} to the corresponding numbers in Series B.")
    elif pattern_in_diffs['type'] == 'Geometric':
        print(f"You can predict numbers in Series A by multiplying the numbers in Series B by a ratio of {pattern_in_diffs['ratio']}.")
    elif pattern_in_diffs['type'] == 'Polynomial':
        print(f"The differences follow a Polynomial pattern of degree {pattern_in_diffs['degree']}.")
        print(f"The sequence of differences is: {pattern_in_diffs['diffs']}")
        print("You would need to use a polynomial function to describe the transformation.")
    else:
        print("There is no simple, common mathematical relationship found between the two series.")

def main():
    """
    Main function to analyze and compare the two number series.
    """
    series_a_date = "08/30/2025"
    series_a_numbers = [3, 18, 22, 27, 33]
    
    series_b_date = "08/27/2025"
    series_b_numbers = [9, 12, 22, 41, 61]
    
    print("--- Analyzing Individual Series ---")
    print(f"Analyzing series from {series_a_date}: {series_a_numbers}")
    pattern_a = find_pattern(series_a_numbers)
    print(f"  Pattern Type: {pattern_a['type']}")
    if 'diffs' in pattern_a:
        print(f"  Differences: {pattern_a['diffs']}")
    
    print("-" * 30)

    print(f"Analyzing series from {series_b_date}: {series_b_numbers}")
    pattern_b = find_pattern(series_b_numbers)
    print(f"  Pattern Type: {pattern_b['type']}")
    if 'diffs' in pattern_b:
        print(f"  Differences: {pattern_b['diffs']}")
    
    print("-" * 30)
    
    print("--- Analyzing Relationship Between Series ---")
    analyze_relationship(series_a_numbers, series_b_numbers)

if __name__ == "__main__":
    main()
