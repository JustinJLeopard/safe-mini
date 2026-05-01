from src.calc import add, median


def check(name, fn):
    try:
        fn()
    except Exception as exc:
        print(f"FAILED {name}: {type(exc).__name__}: {exc}")
        raise
    else:
        print(f"PASSED {name}")


def main():
    check("test_adds_positive_numbers", lambda: assert_equal(add(2, 3), 5))
    check("test_adds_negative_numbers", lambda: assert_equal(add(-2, -3), -5))
    check("test_median_odd_length", lambda: assert_equal(median([7, 1, 3]), 3))
    check(
        "test_median_even_length_average_middle_pair",
        lambda: assert_equal(median([10, 2, 4, 8]), 6),
    )
    try:
        median([])
    except ValueError as exc:
        assert "empty" in str(exc).lower()
        print("PASSED test_median_rejects_empty_list")
    else:
        raise AssertionError("median([]) should raise ValueError")


def assert_equal(actual, expected):
    assert actual == expected, f"expected {expected}, got {actual}"


if __name__ == "__main__":
    main()
