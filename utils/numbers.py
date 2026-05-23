def to_number(x, default=0.0) -> float:
    if x is None:
        return default
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(",", " ")
    try:
        return float(s)
    except ValueError:
        return default
