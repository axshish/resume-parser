
def parse_comma_separated(value: str):
    if not value:
        return []
    parts = [v.strip() for v in value.split(",")]
    return [p for p in parts if p]
