import json
from pathlib import Path

REG_FILE = Path("data/registered_users.json")

def load_registered_users() -> set[int]:
    if not REG_FILE.exists():
        return set()
    with open(REG_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))

def save_registered_users(users: set[int]):
    with open(REG_FILE, "w", encoding="utf-8") as f:
        json.dump(list(users), f, ensure_ascii=False, indent=2)

def is_registered(user_id: int) -> bool:
    return user_id in load_registered_users()

def register_user(user_id: int):
    users = load_registered_users()
    users.add(user_id)
    save_registered_users(users)
