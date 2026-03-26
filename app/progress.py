import json
from pathlib import Path
import threading
import csv
from datetime import datetime
from typing import List

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR = Path(DATA_DIR).resolve()
PROGRESS_FILE = DATA_DIR / "progress.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"


class ProgressManager:
    def __init__(self, user_manager=None):
        self._lock = threading.Lock()
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        if not PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
                
        if not SESSIONS_FILE.exists():
            with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
                
        self._data = self._load()
        self.user_manager = user_manager

    def _load_sessions(self):
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load(self):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self):
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def update_progress(
        self,
        username: str,
        char: str,
        strokes: List[List[int]],
        correct: bool,
        type: str,
        strokes_match: bool
    ):
        with self._lock:
            if username not in self._data:
                self._data[username] = []

            user_entries = self._data[username]
            entry = next((e for e in user_entries if e["character"] == char), None)

            if not entry:
                entry = {
                    "character": char,
                    "total_attempts": 0,
                    "correct_attempts": 0,
                    "type": type,
                    "result": []
                }
                user_entries.append(entry)

            entry["total_attempts"] += 1
            if correct:
                entry["correct_attempts"] += 1

            attempt_number = entry["total_attempts"]
            entry["result"].append({
                "attempt_number": attempt_number,
                "ts": datetime.now().isoformat(),
                "strokes_sample": strokes,
                "correct": bool(correct),
                "strokes_match": strokes_match,
            })
            self._save()

    def record_session_attempt(self, session_id: str, username: str, char: str, result: dict, type: str):
        """Record attempt metadata under sessions file for session history and CSV export."""
        with self._lock:
            sessions = self._load_sessions()
            sessions.append({
                "session_id": session_id,
                "ts": datetime.now().isoformat(),
                "user": username,
                "char": char,
                "score": result.get("score"),
                "passed": result.get("score", 0) >= 60,
                "attempt": result.get("attempt", 1),
                "feedback": result.get("feedback", ""),
                "type": type,
                "strokes_match": result.get("correct_stroke_order_match", False)
            })
            with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(sessions, f, ensure_ascii=False, indent=2)

    def export_sessions_csv(self, filepath: str):
        sessions = self._load_sessions()
        with open(filepath, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["session_id", "ts", "user", "char", "score", "passed", "attempt", "feedback"])
            for s in sessions:
                writer.writerow([
                    s.get("session_id"), s.get("ts"), s.get("user"), s.get("char"), s.get("score"), s.get("passed"), s.get("attempt"), s.get("feedback"),
                ])

    def get_user_stats(self, username: str):
        return self._data.get(username, {})

    def total_characters_attempted(self, username: str) -> int:
        stats = self.get_user_stats(username)
        return sum(v.get("attempts", 0) for v in stats.values())

    def correct_count(self, username: str) -> int:
        stats = self.get_user_stats(username)
        return sum(v.get("correct", 0) for v in stats.values())

    def accuracy_percentage(self, username: str) -> float:
        attempts = self.total_characters_attempted(username)
        if attempts == 0:
            return 0.0
        return (self.correct_count(username) / attempts) * 100
    
    def get_user_sessions(self, username: str):
        sessions = self._load_sessions()
        return [s for s in sessions if s.get("user") == username]
