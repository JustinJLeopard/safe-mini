from src.calc import add, median


def test_adds_positive_numbers():
    assert add(2, 3) == 5


def test_adds_negative_numbers():
    assert add(-2, -3) == -5


def test_median_odd_length():
    assert median([7, 1, 3]) == 3


def test_median_even_length_average_middle_pair():
    assert median([10, 2, 4, 8]) == 6


def test_median_rejects_empty_list():
    try:
        median([])
    except ValueError as exc:
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("median([]) should raise ValueError")
