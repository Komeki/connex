import json
from pathlib import Path

ADMINS_FILE = Path("data/admins.json")

def load_admins() -> set[int]:
    if not ADMINS_FILE.exists():
        return set()
    with open(ADMINS_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))

def save_admins(admins: set[int]):
    with open(ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(admins), f, ensure_ascii=False, indent=2)
