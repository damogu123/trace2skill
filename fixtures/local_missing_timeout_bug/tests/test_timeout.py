from config_reader import read_timeout


def test_missing_timeout_uses_default():
    assert read_timeout({}) == 30


def test_explicit_timeout_is_used():
    assert read_timeout({"timeout": "5"}) == 5
