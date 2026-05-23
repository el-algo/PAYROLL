from datetime import datetime, timedelta

def week_custom_format(dt: datetime | None = None) -> str:
    if dt is None:
        dt = datetime.today()
    dt = dt - timedelta(days=7)
    monday = dt - timedelta(days=dt.weekday())
    sunday = monday + timedelta(days=6)
    return monday.strftime("%d/%m/%Y -") + sunday.strftime(" %d/%m/%Y")

def get_paydate(dt: datetime | None = None) -> str:
    if dt is None:
        dt = datetime.today()
    weekday = dt.weekday()
    days_ahead = 5 - weekday
    days_behind = - (weekday - 5)
    closest = dt + timedelta(days=days_ahead if abs(days_ahead) <= abs(days_behind) else days_behind)
    return closest.strftime("%d/%m/%Y")
