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

def get_events_page(offset: int, limit: int):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name FROM events ORDER BY id LIMIT ? OFFSET ?", (limit, offset)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

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
