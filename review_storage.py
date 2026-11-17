import sqlite3
from pathlib import Path
from datetime import datetime, timezone

# Database location
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "reviews.db"


def initialize_database():
    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            fraud_probability REAL NOT NULL,
            decision TEXT NOT NULL,
            notes TEXT,
            review_date TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_review(transaction_id, fraud_probability, decision, notes=None):
    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.execute("""
        INSERT INTO reviews (
            transaction_id,
            fraud_probability,
            decision,
            notes,
            review_date
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        transaction_id,
        fraud_probability,
        decision,
        notes,
        datetime.now(timezone.utc).isoformat()
    ))

    connection.commit()
    review_id = cursor.lastrowid
    connection.close()

    return review_id
    