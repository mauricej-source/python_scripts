import math

def analyze_sequence(sequence):
    """
    Analyzes a sequence of numbers to identify a mathematical pattern.

    Args:
        sequence (list): A list of numbers.

    Returns:
        str: A description of the pattern found or a message if no simple pattern is detected.
    """
    if len(sequence) < 2:
        return "Sequence is too short to determine a pattern."

    # Check for an Arithmetic Sequence
    if len(set(sequence[i+1] - sequence[i] for i in range(len(sequence) - 1))) == 1:
        diff = sequence[1] - sequence[0]
        return f"Arithmetic Sequence with common difference of {diff}."

    # Check for a Geometric Sequence
    if len(set(sequence[i+1] / sequence[i] for i in range(len(sequence) - 1) if sequence[i] != 0)) == 1:
        ratio = sequence[1] / sequence[0]
        return f"Geometric Sequence with common ratio of {ratio}."
    
    # Check for a Fibonacci-like Sequence
    if len(sequence) >= 3:
        is_fibonacci_like = all(sequence[i] == sequence[i-1] + sequence[i-2] for i in range(2, len(sequence)))
        if is_fibonacci_like:
            return "Fibonacci-like Sequence."

    # Check for polynomial patterns by analyzing the differences of the sequence
    def find_polynomial_degree(seq):
        if len(seq) < 2:
            return None
        
        diff_sequence = [seq[i+1] - seq[i] for i in range(len(seq) - 1)]
        
        # Check if the differences are constant
        if len(set(diff_sequence)) == 1:
            return 1
            
        # Recursively check the differences of the differences
        degree = find_polynomial_degree(diff_sequence)
        if degree is not None:
            return degree + 1
        return None

    degree = find_polynomial_degree(sequence)
    if degree is not None:
        if degree == 2:
            return "Quadratic Sequence (2nd-order difference is constant)."
        elif degree == 3:
            return "Cubic Sequence (3rd-order difference is constant)."
        else:
            return f"Polynomial Sequence of degree {degree}."

    return "No simple mathematical pattern found."

if __name__ == "__main__":
    series = [3, 18, 22, 27, 33]
    print(f"Analyzing the series: {series}")
    pattern = analyze_sequence(series)
    print(f"Pattern found: {pattern}")
