import matplotlib.pyplot as plt
from io import BytesIO
from .database import load_data

def make_chart():
    db = load_data()
    days = list(db.keys())
    values = list(db.values())

    plt.figure(figsize=(10, 4))
    plt.plot(values, marker='o')
    plt.fill_between(range(len(values)), values, alpha=0.2)
    plt.xticks(range(len(days)), days, rotation=45)
    plt.tight_layout()

    bio = BytesIO()
    plt.savefig(bio, format="png")
    bio.seek(0)
    plt.close()
    return bio
