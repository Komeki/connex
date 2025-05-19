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

PAGE_LIMIT = 5
def get_events_page(page: int, limit: int = PAGE_LIMIT) -> list:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    offset = page * limit
    try:
        cursor.execute(
            "SELECT * FROM events ORDER BY id DESC LIMIT ? OFFSET ?", 
            (limit, offset)
        )
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Ошибка при получении мероприятий: {e}")
        return []

def get_events_count():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM events")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_events_paginated(offset=0, limit=5):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, time FROM events LIMIT ? OFFSET ?", (limit, offset))
    events = cursor.fetchall()
    conn.close()
    return events
