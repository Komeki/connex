import sqlite3
from pathlib import Path
from functools import wraps
from aiogram.types import Message

DB_PATH = Path("data/Alldata.db") 

def load_users(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ? LIMIT 1", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def user(func):
    @wraps(func)
    async def wrapper_user(message: Message, *args, **kwargs):
        if not load_users(message.from_user.id):
            await message.answer("Вы не зарегистрированы в системе — /reg")
            return
        return await func(message, *args, **kwargs)
    return wrapper_user

def load_admins() -> set[int]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM admins")
    rows = cursor.fetchall()
    conn.close()
    return {row[0] for row in rows}

def admin_required(func):
    @wraps(func)
    async def wrapper_admin(message: Message):
        ADMINS = load_admins()
        if message.from_user.id not in ADMINS:
            await message.answer("У вас нет доступа к этой функции.")
            return
        return await func(message)
    return wrapper_admin
