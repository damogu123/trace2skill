from text_title import title_or_default


def test_whitespace_title_uses_default():
    assert title_or_default("   ") == "Untitled"


def test_regular_title_is_normalized():
    assert title_or_default(" hello world ") == "Hello World"
