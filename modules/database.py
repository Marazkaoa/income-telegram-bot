import json
import os
from datetime import datetime

DB_FILE = "data.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return {}
    return json.load(open(DB_FILE))

def save_data(db):
    json.dump(db, open(DB_FILE, "w"), indent=2, ensure_ascii=False)

def add_amount(amount):
    db = load_data()
    day = datetime.now().strftime("%d-%m-%Y")
    db.setdefault(day, 0)
    db[day] += amount
    save_data(db)

def delete_date(day):
    db = load_data()
    if day in db:
        del db[day]
        save_data(db)

def reset_all():
    save_data({})
