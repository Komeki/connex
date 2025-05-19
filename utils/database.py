import sqlite3
from pathlib import Path

DB_FILE = Path("data/events.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            time TEXT,
            location TEXT,
            image_id TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_event(name, description, time, location, image_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO events (name, description, time, location, image_id)
        VALUES (?, ?, ?, ?, ?)
    """, (name, description, time, location, image_id))
    conn.commit()
    conn.close()
