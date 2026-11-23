"""Mémoire locale et tâches, conservées dans une base SQLite."""

import sqlite3
import unicodedata
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from app.ai.base import AIMessage
from app.memory.documents import DocumentIndex


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    done: bool


@dataclass(frozen=True)
class Note:
    id: int
    text: str


def search_key(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


class MemoryStore:
    """Utilise la connexion ouverte par l'interface pour une session locale."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY,
                request TEXT NOT NULL,
                reply TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                search_text TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
            );
        """)

    @classmethod
    def open(cls, path: Path) -> "MemoryStore":
        path = path.expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        try:
            return cls(connection)
        except BaseException:
            connection.close()
            raise

    @cached_property
    def documents(self) -> DocumentIndex:
        return DocumentIndex(self.connection)

    def recent_messages(self, limit: int = 12) -> list[AIMessage]:
        rows = self.connection.execute(
            "SELECT request, reply FROM turns ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [
            message
            for request, reply in reversed(rows)
            for message in (AIMessage("user", request), AIMessage("assistant", reply))
        ]

    def save_turn(self, request: str, reply: str) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO turns (request, reply) VALUES (?, ?)", (request, reply)
            )

    def clear_history(self) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM turns")

    def add_note(self, text: str) -> int:
        text = self._required_text(text)
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO notes (text, search_text) VALUES (?, ?)", (text, search_key(text))
            )
        return cursor.lastrowid

    def find_notes(self, query: str = "", limit: int = 20) -> list[Note]:
        key = search_key(query.strip())
        rows = self.connection.execute(
            """SELECT id, text FROM notes WHERE ? = '' OR instr(search_text, ?) > 0
               ORDER BY id DESC LIMIT ?""",
            (key, key, limit),
        )
        return [Note(*row) for row in rows]

    def delete_note(self, note_id: int) -> bool:
        with self.connection:
            result = self.connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return result.rowcount == 1

    def add_task(self, title: str) -> int:
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO tasks (title) VALUES (?)", (self._required_text(title),)
            )
        return cursor.lastrowid

    def list_tasks(self, include_done: bool = True) -> list[Task]:
        rows = self.connection.execute(
            "SELECT id, title, done FROM tasks WHERE ? OR done = 0 ORDER BY done, id",
            (include_done,),
        )
        return [Task(task_id, title, bool(done)) for task_id, title, done in rows]

    def edit_task(self, task_id: int, title: str) -> bool:
        with self.connection:
            result = self.connection.execute(
                "UPDATE tasks SET title = ? WHERE id = ?", (self._required_text(title), task_id)
            )
        return result.rowcount == 1

    def set_task_done(self, task_id: int, done: bool) -> bool:
        with self.connection:
            result = self.connection.execute(
                "UPDATE tasks SET done = ? WHERE id = ?", (done, task_id)
            )
        return result.rowcount == 1

    def delete_task(self, task_id: int) -> bool:
        with self.connection:
            result = self.connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return result.rowcount == 1

    @staticmethod
    def _required_text(text: str) -> str:
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Un texte est requis.")
        return cleaned
