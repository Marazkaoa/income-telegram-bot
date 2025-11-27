from datetime import datetime
from .database import load_data

def format_vnd(x):
    return f"{x:,} VND"

def sorted_days():
    db = load_data()
    arr = []
    for d, v in db.items():
        try:
            dt = datetime.strptime(d, "%d-%m-%Y")
        except:
            continue
        arr.append((dt, d, v))
    arr.sort()
    return arr

def stats_for_month(mm, yy):
    arr = sorted_days()
    items = [(d, val) for dt, d, val in arr if dt.month == mm and dt.year == yy]
    if not items:
        return None

    total = sum(v for _, v in items)
    best = max(items, key=lambda x: x[1])
    worst = min(items, key=lambda x: x[1])
    avg = total / len(items)

    return {
        "total": total,
        "count_days": len(items),
        "best": best,
        "worst": worst,
        "avg": avg
    }
