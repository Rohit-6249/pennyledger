from datetime import date


def month_bounds(month: str) -> tuple[date, date]:
    """Return [start, end) date bounds for a 'YYYY-MM' month string."""
    year, mon = int(month[:4]), int(month[5:7])
    start = date(year, mon, 1)
    end = date(year + 1, 1, 1) if mon == 12 else date(year, mon + 1, 1)
    return start, end
