from stats_summary import average


def test_empty_average_returns_zero():
    assert average([]) == 0.0


def test_average_of_values():
    assert average([2.0, 4.0, 6.0]) == 4.0
