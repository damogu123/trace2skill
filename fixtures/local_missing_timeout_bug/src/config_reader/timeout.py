def read_timeout(config: dict[str, object]) -> int:
    return int(config["timeout"])
