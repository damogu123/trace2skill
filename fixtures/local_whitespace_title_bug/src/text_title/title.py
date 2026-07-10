def title_or_default(text: str | None, default: str = "Untitled") -> str:
    if text is None:
        return default
    if not text.strip():
        return ""
    return text.strip().title()
