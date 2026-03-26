import json
import threading
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR = Path(DATA_DIR).resolve()
USERS_FILE = DATA_DIR / "users.json"


class UserManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.current_user = None
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not USERS_FILE.exists():
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
        self._users = self._load()

    def _load(self):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._users, f, ensure_ascii=False, indent=2)

    def create_or_get_user(self, username: str):
        with self._lock:
            if username in self._users:
                self.current_user = username
                return self._users[username]
            self._users[username] = {"created": True}
            self._save()
            self.current_user = username
            return self._users[username]
