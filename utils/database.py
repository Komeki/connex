import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('data/Alldata.db')

# Инициализация базы данных 
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Создаем таблицы
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        telegram TEXT,
        full_name TEXT,
        course TEXT,
        faculty TEXT,
        group_num TEXT,
        organisation TEXT,
        registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
        curator INTEGER DEFAULT 0 
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        status_text TEXT NOT NULL
    );
        """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        start_date TEXT NOT NULL,
        duration TEXT,
        location TEXT,
        valid INTEGER DEFAULT 1,
        image_id TEXT,
        curator_id INTEGER,
        FOREIGN KEY (curator_id) REFERENCES users(user_id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        telegram TEXT,
        event_id INTEGER NOT NULL,
        registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
        attended INTEGER DEFAULT 0,
        points INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (event_id) REFERENCES events(id)
    );
    """)
    
    # Добавляем тестовые мероприятия
    test_events = [
        ("Лекция по Python", "Основы программирования", "2025-05-25 15:00", "-", "Ауд. 101", 1, None, 123456789),
        ("Хакатон", "Соревнование по разработке", "2025-05-26 18:00", "-", "Коворкинг", 1, None, 123456789)
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO events (name, description, start_date, duration, location, valid, image_id, curator_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, test_events)
    
    conn.commit()
    conn.close()

def does_user_exists(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ? LIMIT 1", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def is_curator(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM admins WHERE user_id = ? LIMIT 1", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def register_user(
    user_id: int,
    telegram: str,
    full_name: str,
    course: str,
    faculty: str,
    group_num: str,
    organisation: str,
    curator: int
):
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users 
        (user_id, telegram, full_name, course, faculty, group_num, organisation, registration_date, curator)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        telegram,
        full_name,
        course,
        faculty,
        group_num,
        organisation,
        registration_date,
        curator
    ))
    conn.commit()
    conn.close()

def save_admin(user_id: int, full_name: str, status_text: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Добавляем или обновляем запись в таблице admins
    cursor.execute("""
        INSERT OR REPLACE INTO admins (user_id, full_name, status_text)
        VALUES (?, ?, ?)
    """, (user_id, full_name, status_text))

    # Обновляем поле curator в таблице users
    cursor.execute("""
        UPDATE users
        SET curator = 1
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

def get_user_profile(user_id):
    # Получает профиль пользователя 
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT full_name, course, faculty, group_num, registration_date 
    FROM users 
    WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return {
        'full_name': row[0],
        'course': row[1],
        'faculty': row[2],
        'group_num': row[3],
        'registration_date': row[4]
    } if row else None

def get_user_registrations(user_id):
    # Получает регистрации пользователя 
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT events.name, events.start_date, events.location, registrations.attended
    FROM registrations 
    JOIN events ON registrations.event_id = events.id
    WHERE registrations.user_id = ?
    ORDER BY events.start_date DESC
    """, (user_id,))
    registrations = []
    for row in cursor.fetchall():
        registrations.append({
            'event_name': row[0],
            'event_start_date': row[1],
            'event_location': row[2],
            'attended': bool(row[3])
        })
    conn.close()
    return registrations

def calculate_user_activity(user_id):
    # Рассчитывает активность пользователя 
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(attended) as attended,
        SUM(points) as points
    FROM registrations 
    WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return {
        'total_count': row[0] if row and row[0] else 0,
        'attended_count': row[1] if row and row[1] else 0,
        'missed_count': (row[0] - row[1]) if row and row[0] else 0,
        'attendance_rate': round(row[1] / row[0] * 100, 2) if row and row[0] else 0,
        'total_points': row[2] if row and row[2] else 0
    }

def add_event(name, description, start_date, duration, location, valid, image_id):
    # Добавляет новое мероприятие 
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO events (name, description, start_date, duration, location, valid, image_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, description, start_date, duration, location, valid, image_id))
    conn.commit()
    conn.close()

def get_events_paginated(offset=0, limit=5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, start_date FROM events
        ORDER BY start_date ASC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    events = cursor.fetchall()
    conn.close()
    return events
