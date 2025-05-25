import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('data/Alldata.db')

# Инициализация базы данных 
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        telegram TEXT,
        full_name TEXT,
        course TEXT,
        major TEXT,
        group_num TEXT,
        organisation TEXT,
        registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
        curator INTEGER DEFAULT 0 
    );
    """)
    
    #admins
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        status_text TEXT NOT NULL
    );
        """)
    
    #events
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

    #organisations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organisations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            org_name TEXT NOT NULL,
            org_desc TEXT
        )
    """)

    #majors
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS majors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            major_name TEXT NOT NULL,
            major_desc TEXT
        )
    """)

    #registrations
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
        FOREIGN KEY (telegram) REFERENCES users(telegram),
        FOREIGN KEY (event_id) REFERENCES events(id)
    );
    """)
    
    conn.commit()
    conn.close()

def does_user_exists(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ? LIMIT 1", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def register_user(
    user_id: int,
    telegram: str,
    full_name: str,
    course: str,
    major: str,
    group_num: str,
    organisation: str,
    curator: int
):
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users 
        (user_id, telegram, full_name, course, major, group_num, organisation, registration_date, curator)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        telegram,
        full_name,
        course,
        major,
        group_num,
        organisation,
        registration_date,
        curator
    ))
    conn.commit()
    conn.close()

def get_majors_list():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT major_name FROM majors ORDER BY major_name")
    majors = [row[0] for row in cursor.fetchall()]
    conn.close()
    return majors

def fill_majors():
    majors = [
        ("АФ", "Архитектурный факультет"),
        ("ФД", "Факультет дизайна"),
        ("ФИСПОС", "Факультет инженерных систем и природоохранного строительства"),
        ("СТФ", "Строительно-технологический факультет"),
        ("ФПГС", "Факультет промышленного и гражданского строительства"),
        ("ИАИТ", "Институт автоматики и информационных технологий"),
        ("ИИЭГО", "Институт инженерно-экономического и гуманитарного образования"),
        ("ИНГТ", "Институт нефтегазовых технологий"),
        ("ФПП", "Факультет пищевых производств"),
        ("ИТФ", "Инженерно-технологический факультет"),
        ("ТЭФ", "Теплоэнергетический факультет"),
        ("ФММТ", "Факультет машиностроения, металлургии и транспорта"),
        ("ХТФ", "Химико-технологический факультет"),
        ("ЭТФ", "Электротехнический факультет")
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for short, full in majors:
        cursor.execute(
            "INSERT INTO majors (major_name, major_desc) VALUES (?, ?)", (short, full)
        )
    conn.commit()
    conn.close()

def is_curator(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM admins WHERE user_id = ? LIMIT 1", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

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
    SELECT full_name, course, major, group_num, registration_date 
    FROM users 
    WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return {
        'full_name': row[0],
        'course': row[1],
        'major': row[2],
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

def add_event(name, description, start_date, duration, location, valid, image_id, curator_id):
    # Добавляет новое мероприятие 
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO events (name, description, start_date, duration, location, valid, image_id, curator_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, description, start_date, duration, location, valid, image_id, curator_id))
    conn.commit()
    conn.close()

def get_available_events():
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    conn.row_factory = sqlite3.Row
    cursor.execute("""
        SELECT name, start_date FROM events
        WHERE valid = 1
        ORDER BY start_date ASC
    """)

    events = cursor.fetchall()
    conn.close()
    return events  # список кортежей

def get_event_by_id(event_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, description, start_date, location, image_id
        FROM events
        WHERE id = ?
    """, (event_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_groups(course: int, major: str) -> list[str]:
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT group_num FROM users
        WHERE course = ? AND major = ?
        ORDER BY group_num
    """, (course, major))
    groups = [row[0] for row in cursor.fetchall()]
    conn.close()
    return groups

def get_users_by_filters(filters: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT user_id FROM users WHERE 1=1"
    params = []
    
    if filters.get('courses'):
        query += " AND course IN ({})".format(','.join(['?']*len(filters['courses'])))
        params.extend(filters['courses'])
    
    if filters.get('majors'):
        query += " AND major IN ({})".format(','.join(['?']*len(filters['majors'])))
        params.extend(filters['majors'])
    
    cursor.execute(query, params)
    users = [{'user_id': row[0]} for row in cursor.fetchall()]
    conn.close()
    
    return users

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

def register_user_for_event(user_id: int, telegram: str, event_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO registrations 
        (user_id, telegram, event_id, registration_date, attended, points)
        VALUES (?, ?, ?, datetime('now'), 1, 100)
    """, (user_id, telegram, event_id))
    conn.commit()
    conn.close()

def is_user_registered(user_id: int, event_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM registrations 
        WHERE user_id = ? AND event_id = ?
    """, (user_id, event_id))
    result = cursor.fetchone()
    conn.close()
    return result is not None

import sqlite3
from openpyxl import Workbook
from openpyxl.styles import Font
from datetime import datetime
from pathlib import Path

EXPORT_DIR = Path('data/exports')
EXPORT_DIR.mkdir(exist_ok=True)

def export_registrations_to_excel(event_id: int) -> Path:
    """
    Экспортирует регистрации на мероприятие в Excel-файл
    Возвращает путь к созданному файлу
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Получаем данные о мероприятии для имени файла
    cursor.execute("SELECT name FROM events WHERE id = ?", (event_id,))
    event_name = cursor.fetchone()[0]
    safe_event_name = "".join(c if c.isalnum() else "_" for c in event_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = EXPORT_DIR / f"registrations_{safe_event_name}_{timestamp}.xlsx"
    
    # Получаем данные регистраций
    cursor.execute("""
        SELECT 
            r.id, 
            u.full_name, 
            u.telegram, 
            u.group_num,
            r.registration_date,
            r.attended,
            r.points
        FROM registrations r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.event_id = ?
        ORDER BY r.registration_date
    """, (event_id,))
    
    registrations = cursor.fetchall()
    conn.close()
    
    # Создаем Excel-файл
    wb = Workbook()
    ws = wb.active
    ws.title = "Регистрации"
    
    # Заголовки
    headers = [
        "ID", "ФИО", "Telegram", "Группа", 
        "Дата регистрации", "Посетил", "Баллы"
    ]
    ws.append(headers)
    
    # Стиль для заголовков
    for cell in ws[1]:
        cell.font = Font(bold=True)
    
    # Данные
    for row in registrations:
        ws.append([
            row[0],  # ID
            row[1],  # ФИО
            f"@{row[2]}" if row[2] else "-",  # Telegram
            row[3],  # Группа
            row[4],  # Дата регистрации
            "Да" if row[5] else "Нет",  # Посетил
            row[6]   # Баллы
        ])
    
    # Автонастройка ширины столбцов
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[column_letter].width = adjusted_width
    
    wb.save(filename)
    return filename