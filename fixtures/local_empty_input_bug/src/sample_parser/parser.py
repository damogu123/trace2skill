def parse_items(text: str | None) -> list[str]:
    if text is None:
        return []
    if not text.strip():
        return None
    return [part.strip() for part in text.split(",") if part.strip()]
