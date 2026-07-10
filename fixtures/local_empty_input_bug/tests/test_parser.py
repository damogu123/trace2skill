from sample_parser import parse_items


def test_empty_input_returns_empty_list():
    assert parse_items("") == []


def test_comma_separated_items_are_trimmed():
    assert parse_items(" alpha, beta ,, gamma ") == ["alpha", "beta", "gamma"]
