def add(a, b):
    """Return the sum of two numbers."""
    return a - b


def median(values):
    """Return the median of a non-empty list of numbers."""
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid]
